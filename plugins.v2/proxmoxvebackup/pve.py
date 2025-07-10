import paramiko
import re

def get_pve_status(host, port, username, password, key_file):
    result = {
        "online": False,
        "error": "",
        "cpu_usage": None,
        "load_avg": None,
        "mem_total": None,
        "mem_used": None,
        "mem_usage": None,
        "swap_total": None,
        "swap_used": None,
        "swap_usage": None,
        "disk_total": None,
        "disk_used": None,
        "disk_usage": None,
        "cpu_model": "",
        "cpu_cores": "",
        "kernel": "",
        "pve_version": "",
        "hostname": "",
        "ip": "-",
    }
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_file:
            private_key = paramiko.RSAKey.from_private_key_file(key_file)
            ssh.connect(host, port=port, username=username, pkey=private_key, timeout=5)
        else:
            ssh.connect(host, port=port, username=username, password=password, timeout=5)
        result["online"] = True

        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
        cpu_line = stdout.read().decode()
        m = re.search(r'(\d+\.\d+)\s*id', cpu_line)
        if m:
            result["cpu_usage"] = round(100 - float(m.group(1)), 2)

        stdin, stdout, stderr = ssh.exec_command("cat /proc/loadavg")
        load_line = stdout.read().decode().strip()
        result["load_avg"] = load_line.split()[:3]

        stdin, stdout, stderr = ssh.exec_command("free -m")
        lines = stdout.read().decode().splitlines()
        for line in lines:
            if line.startswith("Mem:"):
                parts = line.split()
                result["mem_total"] = int(parts[1])
                result["mem_used"] = int(parts[2])
                result["mem_usage"] = round(int(parts[2]) / int(parts[1]) * 100, 2)
            if line.startswith("Swap:"):
                parts = line.split()
                result["swap_total"] = int(parts[1])
                result["swap_used"] = int(parts[2])
                result["swap_usage"] = round(int(parts[2]) / int(parts[1]) * 100, 2) if int(parts[1]) else 0

        stdin, stdout, stderr = ssh.exec_command("df -m / | tail -1")
        parts = stdout.read().decode().split()
        if len(parts) >= 5:
            result["disk_total"] = int(parts[1])
            result["disk_used"] = int(parts[2])
            result["disk_usage"] = float(parts[4].replace('%', ''))

        stdin, stdout, stderr = ssh.exec_command("lscpu | grep 'Model name'")
        cpu_model = stdout.read().decode().split(':')[-1].strip()
        result["cpu_model"] = cpu_model
        stdin, stdout, stderr = ssh.exec_command("nproc")
        result["cpu_cores"] = stdout.read().decode().strip()

        stdin, stdout, stderr = ssh.exec_command("uname -r")
        result["kernel"] = stdout.read().decode().strip()
        stdin, stdout, stderr = ssh.exec_command("pveversion")
        result["pve_version"] = stdout.read().decode().strip()
        stdin, stdout, stderr = ssh.exec_command("hostname")
        result["hostname"] = stdout.read().decode().strip()

        # 获取主机IP
        stdin, stdout, stderr = ssh.exec_command("hostname -I")
        ip_output = stdout.read().decode().strip()
        ip = "-"
        if ip_output:
            ip = next((x for x in ip_output.split() if x and not x.startswith("127.")), "-")
        result["ip"] = ip

        ssh.close()
    except Exception as e:
        result["error"] = str(e)
    return result


def get_qemu_status(host, port, username, password, key_file):
    """
    获取所有QEMU虚拟机的详细状态，修复name字段丢失问题
    """
    vms = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_file:
            private_key = paramiko.RSAKey.from_private_key_file(key_file)
            ssh.connect(host, port=port, username=username, pkey=private_key, timeout=5)
        else:
            ssh.connect(host, port=port, username=username, password=password, timeout=5)
        # 优先用 -o 明确字段
        try:
            qm_cmd = "qm list -o vmid,name,status,lock,uptime,cpu,mem,maxmem,disk,maxdisk,pid"
            stdin, stdout, stderr = ssh.exec_command(qm_cmd)
            lines = stdout.read().decode().splitlines()
            if not lines or len(lines) < 2 or 'unknown option' in (lines[0].lower()):
                raise Exception('no -o support')
            headers = re.split(r'\s+', lines[0].strip())
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = re.split(r'\s+', line.strip(), maxsplit=len(headers)-1)
                data = dict(zip(headers, parts))
                name = data.get('name','')
                if not name:
                    # 尝试用正则从 line 里提取括号内名字
                    m = re.search(r'\(([^)]+)\)', line)
                    if m:
                        name = m.group(1)
                if not name:
                    name = f"QEMU-{data.get('vmid','')}"
                vms.append({
                    'vmid': data.get('vmid',''),
                    'name': name,
                    'status': data.get('status',''),
                    'lock': data.get('lock',''),
                    'uptime': data.get('uptime',''),
                    'cpu': data.get('cpu',''),
                    'mem': data.get('mem',''),
                    'maxmem': data.get('maxmem',''),
                    'disk': data.get('disk',''),
                    'maxdisk': data.get('maxdisk',''),
                    'pid': data.get('pid',''),
                    'netin': '',
                    'netout': '',
                    'type': 'qemu',
                })
        except Exception:
            # 兼容老PVE，手动解析
            stdin, stdout, stderr = ssh.exec_command("qm list")
            lines = stdout.read().decode().splitlines()
            if not lines or len(lines) < 2:
                ssh.close()
                return []
            headers = re.split(r'\s+', lines[0].strip())
            for line in lines[1:]:
                if not line.strip():
                    continue
                # 尝试用正则提取 (name)
                m = re.search(r'\(([^)]+)\)', line)
                name = m.group(1) if m else ''
                parts = re.split(r'\s+', line.strip())
                data = dict(zip(headers, parts))
                if not name:
                    name = data.get('Name','')
                if not name:
                    name = f"QEMU-{data.get('VMID','')}"
                vms.append({
                    'vmid': data.get('VMID',''),
                    'name': name,
                    'status': data.get('Status',''),
                    'lock': data.get('Lock',''),
                    'uptime': data.get('Uptime',''),
                    'cpu': data.get('CPU',''),
                    'mem': data.get('Mem',''),
                    'maxmem': data.get('MaxMem',''),
                    'disk': data.get('Disk',''),
                    'maxdisk': data.get('MaxDisk',''),
                    'pid': data.get('Pid',''),
                    'netin': '',
                    'netout': '',
                    'type': 'qemu',
                })
        ssh.close()
    except Exception as e:
        vms.append({'error': str(e)})
    return vms



def get_container_status(host, port, username, password, key_file):
    """
    获取所有LXC容器的详细状态，修复name字段丢失问题
    """
    containers = []
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key_file:
            private_key = paramiko.RSAKey.from_private_key_file(key_file)
            ssh.connect(host, port=port, username=username, pkey=private_key, timeout=5)
        else:
            ssh.connect(host, port=port, username=username, password=password, timeout=5)
        try:
            pct_cmd = "pct list -o vmid,name,status,lock,uptime,cpu,mem,maxmem,swap,maxswap,disk,maxdisk,pid,netin,netout"
            stdin, stdout, stderr = ssh.exec_command(pct_cmd)
            lines = stdout.read().decode().splitlines()
            err = stderr.read().decode().strip()
            if err or (lines and 'Unknown option' in lines[0]):
                raise Exception('no -o support')
            headers = re.split(r'\s+', lines[0].strip())
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = re.split(r'\s+', line.strip(), maxsplit=len(headers)-1)
                data = dict(zip(headers, parts))
                name = data.get('name','')
                if not name:
                    m = re.search(r'\(([^)]+)\)', line)
                    if m:
                        name = m.group(1)
                if not name:
                    name = f"LXC-{data.get('vmid','')}"
                containers.append({
                    'vmid': data.get('vmid',''),
                    'name': name,
                    'status': data.get('status',''),
                    'lock': data.get('lock',''),
                    'uptime': data.get('uptime',''),
                    'cpu': data.get('cpu',''),
                    'mem': data.get('mem',''),
                    'maxmem': data.get('maxmem',''),
                    'swap': data.get('swap',''),
                    'maxswap': data.get('maxswap',''),
                    'disk': data.get('disk',''),
                    'maxdisk': data.get('maxdisk',''),
                    'pid': data.get('pid',''),
                    'netin': data.get('netin',''),
                    'netout': data.get('netout',''),
                    'type': 'lxc',
                })
        except Exception:
            stdin, stdout, stderr = ssh.exec_command("pct list")
            lines = stdout.read().decode().splitlines()
            if not lines or len(lines) < 2:
                ssh.close()
                return []
            headers = re.split(r'\s+', lines[0].strip())
            for line in lines[1:]:
                if not line.strip():
                    continue
                m = re.search(r'\(([^)]+)\)', line)
                name = m.group(1) if m else ''
                parts = re.split(r'\s+', line.strip())
                data = dict(zip(headers, parts))
                if not name:
                    name = data.get('Name','')
                if not name:
                    name = f"LXC-{data.get('VMID','')}"
                containers.append({
                    'vmid': data.get('VMID',''),
                    'name': name,
                    'status': data.get('Status',''),
                    'lock': data.get('Lock',''),
                    'uptime': data.get('Uptime',''),
                    'cpu': data.get('CPU',''),
                    'mem': data.get('Mem',''),
                    'maxmem': data.get('MaxMem',''),
                    'swap': data.get('Swap',''),
                    'maxswap': data.get('MaxSwap',''),
                    'disk': data.get('Disk',''),
                    'maxdisk': data.get('MaxDisk',''),
                    'pid': data.get('Pid',''),
                    'netin': data.get('NetIn',''),
                    'netout': data.get('NetOut',''),
                    'type': 'lxc',
                })
        ssh.close()
    except Exception as e:
        containers.append({'error': str(e)})
    return containers 