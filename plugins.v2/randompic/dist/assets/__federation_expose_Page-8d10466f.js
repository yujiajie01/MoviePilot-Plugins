import { importShared } from './__federation_fn_import-a2e11483.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_b1d69930_lang = '';

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,normalizeClass:_normalizeClass,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,toDisplayString:_toDisplayString,unref:_unref,createBlock:_createBlock} = await importShared('vue');


const _hoisted_1 = { class: "title-actions" };
const _hoisted_2 = { class: "preview-title-left" };
const _hoisted_3 = { class: "preview-title-right" };
const _hoisted_4 = { class: "preview-mode-selector" };
const _hoisted_5 = ["disabled"];
const _hoisted_6 = { class: "preview-container" };
const _hoisted_7 = {
  key: 0,
  class: "preview-loading"
};
const _hoisted_8 = {
  key: 1,
  class: "preview-error"
};
const _hoisted_9 = { class: "mt-4 text-error" };
const _hoisted_10 = {
  key: 2,
  class: "preview-image-container"
};
const _hoisted_11 = ["src", "alt"];
const _hoisted_12 = {
  key: 1,
  class: "preview-placeholder"
};
const _hoisted_13 = ["disabled"];
const _hoisted_14 = { class: "status-item" };
const _hoisted_15 = { class: "status-item" };
const _hoisted_16 = {
  key: 0,
  class: "port-status-text"
};
const _hoisted_17 = { class: "status-item" };
const _hoisted_18 = { class: "status-item" };
const _hoisted_19 = { class: "status-item" };
const _hoisted_20 = { class: "status-item" };
const _hoisted_21 = { class: "stats-grid" };
const _hoisted_22 = { class: "stat-item" };
const _hoisted_23 = { class: "stat-number" };
const _hoisted_24 = { class: "stat-item" };
const _hoisted_25 = { class: "stat-number" };
const _hoisted_26 = { class: "stat-item" };
const _hoisted_27 = { class: "stat-number" };
const _hoisted_28 = { class: "stat-item" };
const _hoisted_29 = {
  class: "stat-number",
  style: {"color":"#ff9800"}
};
const _hoisted_30 = { class: "api-endpoint-card" };
const _hoisted_31 = { class: "api-endpoint-header" };
const _hoisted_32 = { class: "api-endpoint-icon" };
const _hoisted_33 = { class: "api-url-container" };
const _hoisted_34 = { class: "api-url" };
const _hoisted_35 = { class: "api-endpoint-card" };
const _hoisted_36 = { class: "api-endpoint-header" };
const _hoisted_37 = { class: "api-endpoint-icon" };
const _hoisted_38 = { class: "api-url-container" };
const _hoisted_39 = { class: "api-url" };
const _hoisted_40 = { class: "api-endpoint-card" };
const _hoisted_41 = { class: "api-endpoint-header" };
const _hoisted_42 = { class: "api-endpoint-icon" };
const _hoisted_43 = { class: "api-url-container" };
const _hoisted_44 = { class: "api-url" };
const _hoisted_45 = { class: "api-endpoint-card" };
const _hoisted_46 = { class: "api-endpoint-header" };
const _hoisted_47 = { class: "api-endpoint-icon" };
const _hoisted_48 = { class: "api-url-container" };
const _hoisted_49 = { class: "api-url" };

const {ref,reactive,onMounted,computed} = await importShared('vue');


const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: Object, required: true }
},
  emits: ['close', 'switch'],
  setup(__props, { emit: __emit }) {

const currentHost = window.location.hostname;

const props = __props;

// 响应式数据
const status = reactive({
  enable: false,
  port: "",
  pc_path: "",
  mobile_path: "",
  pc_count: 0,
  mobile_count: 0,
  total_count: 0,
  today_visits: 0,
  server_status: "stopped",
  last_error: "",
  listen_ip: "",
  network_image_url_pc: "",
  network_image_url_mobile: "",
});

// 新增：详细统计
const statusDetail = ref({
  local: { pc: 0, mobile: 0 },
  network: { pc: 0, mobile: 0 }
});

const previewType = ref('auto');
const previewImageUrl = ref('');
const previewLoading = ref(false);
const previewError = ref('');

const refreshing = ref(false);
const starting = ref(false);
ref(false);

const successMessage = ref(null);
const errorMessage = ref(null);

// 计算属性
computed(() => {
  return window.innerWidth < 768;
});

// 方法
const showNotification = (text, type = 'success') => {
  if (type === 'success') {
    successMessage.value = text;
    errorMessage.value = null;
  } else {
    errorMessage.value = text;
    successMessage.value = null;
  }
  // 3秒后自动清除消息
  setTimeout(() => {
    successMessage.value = null;
    errorMessage.value = null;
  }, 3000);
};

function getAccessibleIp() {
  const ip = status.listen_ip || 'localhost';
  // 如果 listen_ip 是 127.0.0.1、localhost 或 172.开头（docker bridge），用当前页面的 hostname
  if (
    ip === '127.0.0.1' ||
    ip === 'localhost' ||
    ip.startsWith('172.')
  ) {
    return window.location.hostname;
  }
  return ip;
}

const getApiUrl = (endpoint) => {
  const ip = getAccessibleIp();
  const port = status.port || '8002';
  return `http://${ip}:${port}${endpoint}`;
};

const getPortStatusColor = (portStatus) => {
  switch (portStatus) {
    case 'available':
      return 'success';
    case 'occupied':
      return 'error';
    case 'error':
      return 'warning';
    case 'unknown':
    default:
      return 'grey';
  }
};

const getPortStatusText = (portStatus) => {
  switch (portStatus) {
    case 'available':
      return '可用';
    case 'occupied':
      return '被占用';
    case 'error':
      return '检查失败';
    case 'unknown':
    default:
      return '未知';
  }
};

const refreshStatus = async () => {
  refreshing.value = true;
  try {
    const statusData = await props.api.get('plugin/RandomPic/status');
    Object.assign(status, statusData);
    if (statusData.detail) {
      statusDetail.value = statusData.detail;
    }
    showNotification('状态已刷新', 'success');
  } catch (error) {
    showNotification('刷新状态失败', 'error');
  } finally {
    refreshing.value = false;
  }
};

const loadPreview = async () => {
  if (status.server_status !== 'running' || !status.port) {
    previewError.value = '服务未启动或端口未配置';
    previewLoading.value = false;
    return;
  }
  previewLoading.value = true;
  previewError.value = '';
  try {
    const ip = getAccessibleIp();
    let url = `http://${ip}:${status.port}/random`;
    if (previewType.value !== 'auto') {
      url += `?type=${previewType.value}`;
    }
    url += (url.includes('?') ? '&' : '?') + `t=${Date.now()}`;
    // 先用 new Image() 预加载
    const img = new window.Image();
    img.onload = () => {
      previewImageUrl.value = url;
      previewLoading.value = false;
    };
    img.onerror = () => {
      previewError.value = '图片加载失败';
      previewLoading.value = false;
    };
    img.src = url;
  } catch (error) {
    previewError.value = '加载预览失败';
    previewLoading.value = false;
    showNotification('加载预览失败', 'error');
  }
};

const handlePreviewError = () => {
  previewLoading.value = false;
  previewError.value = '图片加载失败';
};

const switchPreviewType = (type) => {
  if (previewType.value === type) {
    // 如果点击的是当前已选中的类型，则刷新图片
    loadPreview();
  } else {
    // 如果点击的是不同的类型，则切换类型并自动刷新
    previewType.value = type;
    loadPreview();
  }
};

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    showNotification('链接已复制到剪贴板', 'success');
  } catch (err) {
    // 降级方案：使用传统的复制方法
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    showNotification('链接已复制到剪贴板', 'success');
  }
};

const startService = async () => {
  starting.value = true;
  try {
    // 通过API获取当前配置
    const config = await props.api.get('plugin/RandomPic/config');
    config.enable = true;
    await props.api.post('plugin/RandomPic/config', config);
    await refreshStatus();
    showNotification('服务已启动', 'success');
  } catch (error) {
    showNotification('启动服务失败', 'error');
  } finally {
    starting.value = false;
  }
};

// 生命周期
onMounted(async () => {
  await refreshStatus();
  loadPreview();
});

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_card_title = _resolveComponent("v-card-title");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_alert = _resolveComponent("v-alert");

  return (_openBlock(), _createBlock(_component_v_card, {
    flat: "",
    class: "gallery-page"
  }, {
    default: _withCtx(() => [
      _createVNode(_component_v_card_title, { class: "section-title d-flex align-center mb-4" }, {
        default: _withCtx(() => [
          _createVNode(_component_v_icon, {
            class: "mr-2",
            color: "primary",
            size: "28"
          }, {
            default: _withCtx(() => _cache[10] || (_cache[10] = [
              _createTextVNode("mdi-image-multiple")
            ])),
            _: 1,
            __: [10]
          }),
          _cache[17] || (_cache[17] = _createElementVNode("span", { class: "text-h5 font-weight-bold" }, "随机图床状态", -1)),
          _createVNode(_component_v_spacer),
          _createElementVNode("div", _hoisted_1, [
            _createVNode(_component_v_btn, {
              class: "btn-gradient-status",
              size: "small",
              onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('switch')))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { class: "btn-icon" }, {
                  default: _withCtx(() => _cache[11] || (_cache[11] = [
                    _createTextVNode("mdi-cog")
                  ])),
                  _: 1,
                  __: [11]
                }),
                _cache[12] || (_cache[12] = _createElementVNode("span", { class: "btn-text" }, "插件配置", -1))
              ]),
              _: 1,
              __: [12]
            }),
            _createVNode(_component_v_btn, {
              class: "btn-gradient-reset",
              size: "small",
              onClick: startService,
              loading: starting.value
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { class: "btn-icon" }, {
                  default: _withCtx(() => _cache[13] || (_cache[13] = [
                    _createTextVNode("mdi-restart")
                  ])),
                  _: 1,
                  __: [13]
                }),
                _cache[14] || (_cache[14] = _createElementVNode("span", { class: "btn-text" }, "重启服务", -1))
              ]),
              _: 1,
              __: [14]
            }, 8, ["loading"]),
            _createVNode(_component_v_btn, {
              class: "btn-gradient-close",
              size: "small",
              onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('close')))
            }, {
              default: _withCtx(() => [
                _createVNode(_component_v_icon, { class: "btn-icon" }, {
                  default: _withCtx(() => _cache[15] || (_cache[15] = [
                    _createTextVNode("mdi-close")
                  ])),
                  _: 1,
                  __: [15]
                }),
                _cache[16] || (_cache[16] = _createElementVNode("span", { class: "btn-text" }, "关闭", -1))
              ]),
              _: 1,
              __: [16]
            })
          ])
        ]),
        _: 1,
        __: [17]
      }),
      _createVNode(_component_v_row, {
        class: "main-content",
        align: "stretch"
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_col, {
            cols: "12",
            md: "8"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card, {
                class: "glass-card preview-card",
                elevation: "4"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "preview-title-container" }, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_2, [
                        _createVNode(_component_v_icon, {
                          color: "primary",
                          size: "24",
                          class: "mr-2"
                        }, {
                          default: _withCtx(() => _cache[18] || (_cache[18] = [
                            _createTextVNode("mdi-image-search")
                          ])),
                          _: 1,
                          __: [18]
                        }),
                        _cache[19] || (_cache[19] = _createElementVNode("span", null, "图片预览", -1))
                      ]),
                      _createElementVNode("div", _hoisted_3, [
                        _createElementVNode("div", _hoisted_4, [
                          _createElementVNode("button", {
                            class: _normalizeClass(['mode-btn', previewType.value === 'pc' ? 'mode-btn-active' : '']),
                            onClick: _cache[2] || (_cache[2] = $event => (switchPreviewType('pc')))
                          }, [
                            _createVNode(_component_v_icon, {
                              size: "16",
                              class: "mode-icon"
                            }, {
                              default: _withCtx(() => _cache[20] || (_cache[20] = [
                                _createTextVNode("mdi-monitor")
                              ])),
                              _: 1,
                              __: [20]
                            }),
                            _cache[21] || (_cache[21] = _createElementVNode("span", { class: "mode-text" }, "横屏", -1))
                          ], 2),
                          _createElementVNode("button", {
                            class: _normalizeClass(['mode-btn', previewType.value === 'mobile' ? 'mode-btn-active' : '']),
                            onClick: _cache[3] || (_cache[3] = $event => (switchPreviewType('mobile')))
                          }, [
                            _createVNode(_component_v_icon, {
                              size: "16",
                              class: "mode-icon"
                            }, {
                              default: _withCtx(() => _cache[22] || (_cache[22] = [
                                _createTextVNode("mdi-cellphone")
                              ])),
                              _: 1,
                              __: [22]
                            }),
                            _cache[23] || (_cache[23] = _createElementVNode("span", { class: "mode-text" }, "竖屏", -1))
                          ], 2),
                          _createElementVNode("button", {
                            class: _normalizeClass(['mode-btn', previewType.value === 'auto' ? 'mode-btn-active' : '']),
                            onClick: _cache[4] || (_cache[4] = $event => (switchPreviewType('auto')))
                          }, [
                            _createVNode(_component_v_icon, {
                              size: "16",
                              class: "mode-icon"
                            }, {
                              default: _withCtx(() => _cache[24] || (_cache[24] = [
                                _createTextVNode("mdi-auto-fix")
                              ])),
                              _: 1,
                              __: [24]
                            }),
                            _cache[25] || (_cache[25] = _createElementVNode("span", { class: "mode-text" }, "自动", -1))
                          ], 2),
                          _cache[28] || (_cache[28] = _createElementVNode("div", { class: "mode-separator" }, null, -1)),
                          _createElementVNode("button", {
                            class: "mode-btn mode-btn-refresh",
                            onClick: loadPreview,
                            disabled: previewLoading.value
                          }, [
                            _createVNode(_component_v_icon, {
                              size: "16",
                              class: _normalizeClass(["mode-icon", { 'rotating': previewLoading.value }])
                            }, {
                              default: _withCtx(() => _cache[26] || (_cache[26] = [
                                _createTextVNode("mdi-refresh")
                              ])),
                              _: 1,
                              __: [26]
                            }, 8, ["class"]),
                            _cache[27] || (_cache[27] = _createElementVNode("span", { class: "mode-text" }, "刷新", -1))
                          ], 8, _hoisted_5)
                        ])
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_6, [
                        (previewLoading.value && !previewImageUrl.value)
                          ? (_openBlock(), _createElementBlock("div", _hoisted_7, [
                              _createVNode(_component_v_progress_circular, {
                                indeterminate: "",
                                color: "primary",
                                size: "64"
                              }),
                              _cache[29] || (_cache[29] = _createElementVNode("div", { class: "mt-4" }, "正在加载图片...", -1))
                            ]))
                          : (previewError.value)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_8, [
                                _createVNode(_component_v_icon, {
                                  color: "error",
                                  size: "64"
                                }, {
                                  default: _withCtx(() => _cache[30] || (_cache[30] = [
                                    _createTextVNode("mdi-image-broken")
                                  ])),
                                  _: 1,
                                  __: [30]
                                }),
                                _createElementVNode("div", _hoisted_9, _toDisplayString(previewError.value), 1),
                                _createVNode(_component_v_btn, {
                                  color: "primary",
                                  onClick: loadPreview,
                                  class: "mt-4"
                                }, {
                                  default: _withCtx(() => _cache[31] || (_cache[31] = [
                                    _createTextVNode("重试")
                                  ])),
                                  _: 1,
                                  __: [31]
                                })
                              ]))
                            : (_openBlock(), _createElementBlock("div", _hoisted_10, [
                                (previewImageUrl.value)
                                  ? (_openBlock(), _createElementBlock("img", {
                                      key: 0,
                                      src: previewImageUrl.value,
                                      alt: '随机图片预览 - ' + previewType.value,
                                      class: "preview-image",
                                      onLoad: _cache[5] || (_cache[5] = $event => (previewLoading.value = false)),
                                      onError: handlePreviewError
                                    }, null, 40, _hoisted_11))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_12, [
                                      _createVNode(_component_v_icon, {
                                        color: "grey",
                                        size: "64"
                                      }, {
                                        default: _withCtx(() => _cache[32] || (_cache[32] = [
                                          _createTextVNode("mdi-image")
                                        ])),
                                        _: 1,
                                        __: [32]
                                      }),
                                      _cache[33] || (_cache[33] = _createElementVNode("div", { class: "mt-4 text-grey" }, "点击下方按钮预览图片", -1))
                                    ]))
                              ]))
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_v_col, {
            cols: "12",
            md: "4",
            style: {"height":"600px"}
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_row, {
                class: "status-cards-vertical",
                dense: ""
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_col, { cols: "12" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_card, {
                        class: "glass-card",
                        elevation: "4",
                        style: {"height":"189px !important","min-height":"189px !important"}
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                color: status.server_status === 'running' ? 'success' : 'grey',
                                size: "24",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(status.server_status === 'running' ? 'mdi-server-network' : 'mdi-server-off'), 1)
                                ]),
                                _: 1
                              }, 8, ["color"]),
                              _cache[35] || (_cache[35] = _createElementVNode("span", null, "服务状态", -1)),
                              _createVNode(_component_v_spacer),
                              _createElementVNode("button", {
                                class: "mode-btn status-refresh-btn",
                                onClick: refreshStatus,
                                disabled: refreshing.value
                              }, [
                                _createVNode(_component_v_icon, {
                                  size: "16",
                                  class: _normalizeClass(["mode-icon", { 'rotating': refreshing.value }])
                                }, {
                                  default: _withCtx(() => _cache[34] || (_cache[34] = [
                                    _createTextVNode("mdi-refresh")
                                  ])),
                                  _: 1,
                                  __: [34]
                                }, 8, ["class"])
                              ], 8, _hoisted_13)
                            ]),
                            _: 1,
                            __: [35]
                          }),
                          _createVNode(_component_v_card_text, null, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_14, [
                                _cache[36] || (_cache[36] = _createElementVNode("span", { class: "label" }, "运行状态：", -1)),
                                _createVNode(_component_v_chip, {
                                  color: status.server_status === 'running' ? 'success' : 'grey',
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(status.server_status === 'running' ? '已启用' : '已禁用'), 1)
                                  ]),
                                  _: 1
                                }, 8, ["color"])
                              ]),
                              _createElementVNode("div", _hoisted_15, [
                                _cache[37] || (_cache[37] = _createElementVNode("span", { class: "label" }, "服务端口：", -1)),
                                _createVNode(_component_v_chip, {
                                  color: getPortStatusColor(status.port_status),
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(status.port || '未配置') + " ", 1),
                                    (status.port_status !== 'unknown' && status.port)
                                      ? (_openBlock(), _createElementBlock("span", _hoisted_16, " /" + _toDisplayString(getPortStatusText(status.port_status)), 1))
                                      : _createCommentVNode("", true)
                                  ]),
                                  _: 1
                                }, 8, ["color"])
                              ]),
                              _createElementVNode("div", _hoisted_17, [
                                _cache[38] || (_cache[38] = _createElementVNode("span", { class: "label" }, "服务监听IP：", -1)),
                                _createVNode(_component_v_chip, {
                                  color: "info",
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(_unref(currentHost) || '-'), 1)
                                  ]),
                                  _: 1
                                })
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, { cols: "12" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_card, {
                        class: "glass-card",
                        elevation: "4",
                        style: {"height":"189px !important","min-height":"189px !important"}
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                color: "info",
                                size: "24",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[39] || (_cache[39] = [
                                  _createTextVNode("mdi-folder-check")
                                ])),
                                _: 1,
                                __: [39]
                              }),
                              _cache[40] || (_cache[40] = _createElementVNode("span", null, "目录监控", -1))
                            ]),
                            _: 1,
                            __: [40]
                          }),
                          _createVNode(_component_v_card_text, null, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_18, [
                                _cache[41] || (_cache[41] = _createElementVNode("span", { class: "label" }, "横屏目录：", -1)),
                                _createVNode(_component_v_chip, {
                                  color: (status.pc_path || status.network_image_url_pc) ? 'success' : 'error',
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString((status.pc_path || status.network_image_url_pc) ? '已配置' : '未配置'), 1)
                                  ]),
                                  _: 1
                                }, 8, ["color"])
                              ]),
                              _createElementVNode("div", _hoisted_19, [
                                _cache[42] || (_cache[42] = _createElementVNode("span", { class: "label" }, "竖屏目录：", -1)),
                                _createVNode(_component_v_chip, {
                                  color: (status.mobile_path || status.network_image_url_mobile) ? 'success' : 'error',
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString((status.mobile_path || status.network_image_url_mobile) ? '已配置' : '未配置'), 1)
                                  ]),
                                  _: 1
                                }, 8, ["color"])
                              ]),
                              _createElementVNode("div", _hoisted_20, [
                                _cache[43] || (_cache[43] = _createElementVNode("span", { class: "label" }, "配置完整性：", -1)),
                                _createVNode(_component_v_chip, {
                                  color: status.pc_path && status.mobile_path ? 'success' : 'warning',
                                  size: "small"
                                }, {
                                  default: _withCtx(() => [
                                    _createTextVNode(_toDisplayString(status.pc_path && status.mobile_path ? '完整' : '不完整'), 1)
                                  ]),
                                  _: 1
                                }, 8, ["color"])
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_col, { cols: "12" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_card, {
                        class: "glass-card",
                        elevation: "4",
                        style: {"height":"190px !important","min-height":"190px !important"}
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                            default: _withCtx(() => [
                              _createVNode(_component_v_icon, {
                                color: "info",
                                size: "24",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[44] || (_cache[44] = [
                                  _createTextVNode("mdi-image")
                                ])),
                                _: 1,
                                __: [44]
                              }),
                              _cache[45] || (_cache[45] = _createElementVNode("span", null, "图片统计", -1))
                            ]),
                            _: 1,
                            __: [45]
                          }),
                          _createVNode(_component_v_card_text, null, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_21, [
                                _createElementVNode("div", _hoisted_22, [
                                  _createElementVNode("div", _hoisted_23, _toDisplayString(status.total_count || 0), 1),
                                  _cache[46] || (_cache[46] = _createElementVNode("div", { class: "stat-label" }, "总图片数", -1))
                                ]),
                                _createElementVNode("div", _hoisted_24, [
                                  _createElementVNode("div", _hoisted_25, _toDisplayString(status.pc_count || 0), 1),
                                  _cache[47] || (_cache[47] = _createElementVNode("div", { class: "stat-label" }, "横屏图片", -1))
                                ]),
                                _createElementVNode("div", _hoisted_26, [
                                  _createElementVNode("div", _hoisted_27, _toDisplayString(status.mobile_count || 0), 1),
                                  _cache[48] || (_cache[48] = _createElementVNode("div", { class: "stat-label" }, "竖屏图片", -1))
                                ]),
                                _createElementVNode("div", _hoisted_28, [
                                  _createElementVNode("div", _hoisted_29, _toDisplayString(status.today_visits), 1),
                                  _cache[49] || (_cache[49] = _createElementVNode("div", { class: "stat-label" }, "今日访问", -1))
                                ])
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      _createVNode(_component_v_row, { class: "mb-6 api-row" }, {
        default: _withCtx(() => [
          _createVNode(_component_v_col, { cols: "12" }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card, {
                class: "glass-card",
                elevation: "4"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        color: "success",
                        size: "24",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => _cache[50] || (_cache[50] = [
                          _createTextVNode("mdi-api")
                        ])),
                        _: 1,
                        __: [50]
                      }),
                      _cache[51] || (_cache[51] = _createElementVNode("span", null, "API 接口", -1))
                    ]),
                    _: 1,
                    __: [51]
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_row, null, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_30, [
                                _createElementVNode("div", _hoisted_31, [
                                  _createElementVNode("div", _hoisted_32, [
                                    _createVNode(_component_v_icon, {
                                      color: "primary",
                                      size: "24"
                                    }, {
                                      default: _withCtx(() => _cache[52] || (_cache[52] = [
                                        _createTextVNode("mdi-web")
                                      ])),
                                      _: 1,
                                      __: [52]
                                    })
                                  ]),
                                  _cache[53] || (_cache[53] = _createElementVNode("div", { class: "api-endpoint-info" }, [
                                    _createElementVNode("h3", { class: "api-endpoint-title" }, "自动识别设备"),
                                    _createElementVNode("p", { class: "api-endpoint-desc" }, "根据设备类型自动返回横屏或竖屏图片")
                                  ], -1))
                                ]),
                                _createElementVNode("div", _hoisted_33, [
                                  _createElementVNode("div", _hoisted_34, _toDisplayString(getApiUrl('/random')), 1),
                                  _createElementVNode("button", {
                                    class: "api-copy-btn",
                                    onClick: _cache[6] || (_cache[6] = $event => (copyToClipboard(getApiUrl('/random')))),
                                    title: "复制链接"
                                  }, [
                                    _createVNode(_component_v_icon, { size: "16" }, {
                                      default: _withCtx(() => _cache[54] || (_cache[54] = [
                                        _createTextVNode("mdi-content-copy")
                                      ])),
                                      _: 1,
                                      __: [54]
                                    })
                                  ])
                                ])
                              ])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_35, [
                                _createElementVNode("div", _hoisted_36, [
                                  _createElementVNode("div", _hoisted_37, [
                                    _createVNode(_component_v_icon, {
                                      color: "success",
                                      size: "24"
                                    }, {
                                      default: _withCtx(() => _cache[55] || (_cache[55] = [
                                        _createTextVNode("mdi-monitor")
                                      ])),
                                      _: 1,
                                      __: [55]
                                    })
                                  ]),
                                  _cache[56] || (_cache[56] = _createElementVNode("div", { class: "api-endpoint-info" }, [
                                    _createElementVNode("h3", { class: "api-endpoint-title" }, "指定横屏图片"),
                                    _createElementVNode("p", { class: "api-endpoint-desc" }, "强制返回横屏图片")
                                  ], -1))
                                ]),
                                _createElementVNode("div", _hoisted_38, [
                                  _createElementVNode("div", _hoisted_39, _toDisplayString(getApiUrl('/random?type=pc')), 1),
                                  _createElementVNode("button", {
                                    class: "api-copy-btn",
                                    onClick: _cache[7] || (_cache[7] = $event => (copyToClipboard(getApiUrl('/random?type=pc')))),
                                    title: "复制链接"
                                  }, [
                                    _createVNode(_component_v_icon, { size: "16" }, {
                                      default: _withCtx(() => _cache[57] || (_cache[57] = [
                                        _createTextVNode("mdi-content-copy")
                                      ])),
                                      _: 1,
                                      __: [57]
                                    })
                                  ])
                                ])
                              ])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_40, [
                                _createElementVNode("div", _hoisted_41, [
                                  _createElementVNode("div", _hoisted_42, [
                                    _createVNode(_component_v_icon, {
                                      color: "warning",
                                      size: "24"
                                    }, {
                                      default: _withCtx(() => _cache[58] || (_cache[58] = [
                                        _createTextVNode("mdi-cellphone")
                                      ])),
                                      _: 1,
                                      __: [58]
                                    })
                                  ]),
                                  _cache[59] || (_cache[59] = _createElementVNode("div", { class: "api-endpoint-info" }, [
                                    _createElementVNode("h3", { class: "api-endpoint-title" }, "指定竖屏图片"),
                                    _createElementVNode("p", { class: "api-endpoint-desc" }, "强制返回竖屏图片")
                                  ], -1))
                                ]),
                                _createElementVNode("div", _hoisted_43, [
                                  _createElementVNode("div", _hoisted_44, _toDisplayString(getApiUrl('/random?type=mobile')), 1),
                                  _createElementVNode("button", {
                                    class: "api-copy-btn",
                                    onClick: _cache[8] || (_cache[8] = $event => (copyToClipboard(getApiUrl('/random?type=mobile')))),
                                    title: "复制链接"
                                  }, [
                                    _createVNode(_component_v_icon, { size: "16" }, {
                                      default: _withCtx(() => _cache[60] || (_cache[60] = [
                                        _createTextVNode("mdi-content-copy")
                                      ])),
                                      _: 1,
                                      __: [60]
                                    })
                                  ])
                                ])
                              ])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_45, [
                                _createElementVNode("div", _hoisted_46, [
                                  _createElementVNode("div", _hoisted_47, [
                                    _createVNode(_component_v_icon, {
                                      color: "info",
                                      size: "24"
                                    }, {
                                      default: _withCtx(() => _cache[61] || (_cache[61] = [
                                        _createTextVNode("mdi-chart-bar")
                                      ])),
                                      _: 1,
                                      __: [61]
                                    })
                                  ]),
                                  _cache[62] || (_cache[62] = _createElementVNode("div", { class: "api-endpoint-info" }, [
                                    _createElementVNode("h3", { class: "api-endpoint-title" }, "统计数据"),
                                    _createElementVNode("p", { class: "api-endpoint-desc" }, "获取图片数量和访问统计")
                                  ], -1))
                                ]),
                                _createElementVNode("div", _hoisted_48, [
                                  _createElementVNode("div", _hoisted_49, _toDisplayString(getApiUrl('/stats')), 1),
                                  _createElementVNode("button", {
                                    class: "api-copy-btn",
                                    onClick: _cache[9] || (_cache[9] = $event => (copyToClipboard(getApiUrl('/stats')))),
                                    title: "复制链接"
                                  }, [
                                    _createVNode(_component_v_icon, { size: "16" }, {
                                      default: _withCtx(() => _cache[63] || (_cache[63] = [
                                        _createTextVNode("mdi-content-copy")
                                      ])),
                                      _: 1,
                                      __: [63]
                                    })
                                  ])
                                ])
                              ])
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      _createVNode(_component_v_divider),
      (successMessage.value)
        ? (_openBlock(), _createBlock(_component_v_alert, {
            key: 0,
            type: "success",
            density: "compact",
            class: "mb-2 text-caption",
            variant: "tonal",
            closable: ""
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(successMessage.value), 1)
            ]),
            _: 1
          }))
        : _createCommentVNode("", true),
      (errorMessage.value)
        ? (_openBlock(), _createBlock(_component_v_alert, {
            key: 1,
            type: "error",
            density: "compact",
            class: "mb-2 text-caption",
            variant: "tonal",
            closable: ""
          }, {
            default: _withCtx(() => [
              _createTextVNode(_toDisplayString(errorMessage.value), 1)
            ]),
            _: 1
          }))
        : _createCommentVNode("", true)
    ]),
    _: 1
  }))
}
}

};
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-b1d69930"]]);

export { PageComponent as default };
