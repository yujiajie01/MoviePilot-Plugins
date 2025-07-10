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


def get_node_name(ssh):
    stdin, stdout, stderr = ssh.exec_command('hostname')
    return stdout.read().decode().strip()


def get_qemu_status(host, port, username, password, key_file):
    """
    获取所有QEMU虚拟机的详细状态，补充displayName和tags字段。
    tags 字段通过 qm config <vmid> 解析 tags: 行获得。
    uptime 字段通过 pvesh 命令获取。
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
        try:
            node_name = get_node_name(ssh)
            stdin, stdout, stderr = ssh.exec_command("qm list")
            lines = stdout.read().decode().splitlines()
            if not lines or len(lines) < 2:
                ssh.close()
                return []
            headers = [h.lower() for h in re.split(r'\s+', lines[0].strip())]
            for line in lines[1:]:
                if not line.strip():
                    continue
                m = re.search(r'\(([^)]+)\)', line)
                name = m.group(1) if m else ''
                parts = re.split(r'\s+', line.strip())
                data = dict(zip(headers, parts))
                if not name:
                    name = data.get('name','')
                if not name:
                    name = f"QEMU-{data.get('vmid','')}"
                display_name = name
                tags = ''
                vmid = data.get('vmid','')
                # 解析 displayName和tags
                if vmid:
                    try:
                        stdin2, stdout2, stderr2 = ssh.exec_command(f"qm config {vmid}")
                        config_lines = stdout2.read().decode().splitlines()
                        for cl in config_lines:
                            if cl.startswith('name:'):
                                real_name = cl.split(':',1)[1].strip()
                                if real_name:
                                    display_name = real_name
                        for cl in config_lines:
                            if cl.startswith('tags:'):
                                tags = cl.split(':',1)[1].strip()
                                break
                    except Exception:
                        tags = ''
                # 用paramiko invoke_shell方式获取uptime，兼容极端受限环境
                uptime = 0
                if vmid:
                    try:
                        import json
                        stdin_uptime, stdout_uptime, stderr_uptime = ssh.exec_command(f"/usr/bin/pvesh get /nodes/{node_name}/qemu/{vmid}/status/current --output-format json")
                        output = stdout_uptime.read().decode()
                        data_json = json.loads(output)
                        uptime = data_json.get('uptime', '')
                    except Exception as e:
                        uptime = 0
                status = data.get('status','')
                if not status:
                    vmid = data.get('vmid','')
                    if vmid:
                        try:
                            stdin3, stdout3, stderr3 = ssh.exec_command(f"qm status {vmid}")
                            status_line = stdout3.read().decode().strip()
                            m = re.search(r'status:\s*(\w+)', status_line)
                            if m:
                                status = m.group(1)
                        except Exception:
                            pass
                vms.append({
                    'vmid': data.get('vmid',''),
                    'name': name,
                    'displayName': display_name,
                    'status': status,
                    'lock': data.get('lock',''),
                    'uptime': uptime,
                    'cpu': data.get('cpu',''),
                    'mem': data.get('mem',''),
                    'maxmem': data.get('maxmem',''),
                    'disk': data.get('disk',''),
                    'maxdisk': data.get('maxdisk',''),
                    'pid': data.get('pid',''),
                    'netin': '',
                    'netout': '',
                    'type': 'qemu',
                    'tags': tags
                })
        except Exception as e:
            vms.append({'error': str(e)})
        ssh.close()
    except Exception as e:
        vms.append({'error': str(e)})
    return vms


def get_container_status(host, port, username, password, key_file):
    """
    获取所有LXC容器的详细状态，补充displayName和tags字段。
    tags 字段通过 pct config <vmid> 解析 tags: 行获得。
    uptime 字段通过 pvesh 命令获取。
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
            node_name = get_node_name(ssh)
            stdin, stdout, stderr = ssh.exec_command("pct list")
            lines = stdout.read().decode().splitlines()
            if not lines or len(lines) < 2:
                ssh.close()
                return []
            headers = [h.lower() for h in re.split(r'\s+', lines[0].strip())]
            for line in lines[1:]:
                if not line.strip():
                    continue
                m = re.search(r'\(([^)]+)\)', line)
                name = m.group(1) if m else ''
                parts = re.split(r'\s+', line.strip())
                data = dict(zip(headers, parts))
                if not name:
                    name = data.get('name','')
                if not name:
                    name = f"LXC-{data.get('vmid','')}"
                display_name = name
                tags = ''
                uptime = 0
                vmid = data.get('vmid','')
                if name.startswith('LXC-'):
                    try:
                        stdin2, stdout2, stderr2 = ssh.exec_command(f"pct config {vmid}")
                        config_lines = stdout2.read().decode().splitlines()
                        for cl in config_lines:
                            if cl.startswith('hostname:'):
                                real_name = cl.split(':',1)[1].strip()
                                if real_name:
                                    display_name = real_name
                        for cl in config_lines:
                            if cl.startswith('tags:'):
                                tags = cl.split(':',1)[1].strip()
                                break
                    except Exception:
                        tags = ''
                # 用paramiko invoke_shell方式获取uptime，兼容极端受限环境
                if vmid:
                    try:
                        import json
                        stdin_uptime, stdout_uptime, stderr_uptime = ssh.exec_command(f"/usr/bin/pvesh get /nodes/{node_name}/lxc/{vmid}/status/current --output-format json")
                        output = stdout_uptime.read().decode()
                        data_json = json.loads(output)
                        uptime = data_json.get('uptime', '')
                    except Exception as e:
                        uptime = 0
                status = data.get('status','')
                if not status:
                    vmid = data.get('vmid','')
                    if vmid:
                        try:
                            stdin3, stdout3, stderr3 = ssh.exec_command(f"pct status {vmid}")
                            status_line = stdout3.read().decode().strip()
                            m = re.search(r'status:\s*(\w+)', status_line)
                            if m:
                                status = m.group(1)
                        except Exception:
                            pass
                containers.append({
                    'vmid': data.get('vmid',''),
                    'name': name,
                    'displayName': display_name,
                    'status': status,
                    'lock': data.get('lock',''),
                    'uptime': uptime,
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
                    'tags': tags
                })
        except Exception as e:
            containers.append({'error': str(e)})
        ssh.close()
    except Exception as e:
        containers.append({'error': str(e)})
    return containers 