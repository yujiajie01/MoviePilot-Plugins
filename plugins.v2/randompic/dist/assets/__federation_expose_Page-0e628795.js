import { importShared } from './__federation_fn_import-a2e11483.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Page_vue_vue_type_style_index_0_scoped_893caf23_lang = '';

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,toDisplayString:_toDisplayString,unref:_unref,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "status-item" };
const _hoisted_2 = { class: "status-item" };
const _hoisted_3 = { class: "status-item" };
const _hoisted_4 = { class: "status-item" };
const _hoisted_5 = { class: "status-item" };
const _hoisted_6 = { class: "status-item" };
const _hoisted_7 = { class: "stats-grid" };
const _hoisted_8 = { class: "stat-item" };
const _hoisted_9 = { class: "stat-number" };
const _hoisted_10 = { key: 0 };
const _hoisted_11 = { key: 1 };
const _hoisted_12 = { class: "stat-item" };
const _hoisted_13 = { class: "stat-number" };
const _hoisted_14 = { key: 0 };
const _hoisted_15 = { key: 1 };
const _hoisted_16 = { class: "stat-item" };
const _hoisted_17 = { class: "stat-number" };
const _hoisted_18 = { key: 0 };
const _hoisted_19 = { key: 1 };
const _hoisted_20 = { class: "stat-item" };
const _hoisted_21 = {
  class: "stat-number",
  style: {"color":"#ff9800"}
};
const _hoisted_22 = { class: "action-buttons" };
const _hoisted_23 = { class: "preview-container" };
const _hoisted_24 = {
  key: 0,
  class: "preview-loading"
};
const _hoisted_25 = {
  key: 1,
  class: "preview-error"
};
const _hoisted_26 = { class: "mt-4 text-error" };
const _hoisted_27 = {
  key: 2,
  class: "preview-image-container"
};
const _hoisted_28 = ["src", "alt"];
const _hoisted_29 = {
  key: 1,
  class: "preview-placeholder"
};
const _hoisted_30 = { class: "api-endpoint" };
const _hoisted_31 = { class: "endpoint-title" };
const _hoisted_32 = { class: "api-url" };
const _hoisted_33 = { class: "api-endpoint" };
const _hoisted_34 = { class: "endpoint-title" };
const _hoisted_35 = { class: "api-url" };
const _hoisted_36 = { class: "api-endpoint" };
const _hoisted_37 = { class: "endpoint-title" };
const _hoisted_38 = { class: "api-url" };
const _hoisted_39 = { class: "api-endpoint" };
const _hoisted_40 = { class: "endpoint-title" };
const _hoisted_41 = { class: "api-url" };

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
  enabled: false,
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

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
});

// 计算属性
const isMobile = computed(() => {
  return window.innerWidth < 768;
});

// 方法
const showNotification = (text, color = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
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
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_card = _resolveComponent("v-card");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_btn_group = _resolveComponent("v-btn-group");
  const _component_v_progress_circular = _resolveComponent("v-progress-circular");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
  const _component_v_divider = _resolveComponent("v-divider");
  const _component_v_snackbar = _resolveComponent("v-snackbar");

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
            default: _withCtx(() => _cache[7] || (_cache[7] = [
              _createTextVNode("mdi-image-multiple")
            ])),
            _: 1,
            __: [7]
          }),
          _cache[9] || (_cache[9] = _createElementVNode("span", { class: "text-h5 font-weight-bold" }, "随机图库状态", -1)),
          _createVNode(_component_v_spacer),
          (isMobile.value)
            ? (_openBlock(), _createBlock(_component_v_btn, {
                key: 0,
                icon: "",
                class: "close-btn",
                onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('close')))
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_icon, {
                    size: "28",
                    color: "grey"
                  }, {
                    default: _withCtx(() => _cache[8] || (_cache[8] = [
                      _createTextVNode("mdi-close")
                    ])),
                    _: 1,
                    __: [8]
                  })
                ]),
                _: 1
              }))
            : _createCommentVNode("", true)
        ]),
        _: 1,
        __: [9]
      }),
      _createVNode(_component_v_row, {
        class: "mb-6",
        align: "stretch",
        dense: ""
      }, {
        default: _withCtx(() => [
          _createVNode(_component_v_col, {
            cols: "12",
            md: "3"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card, {
                class: "glass-card",
                elevation: "4"
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
                      _cache[11] || (_cache[11] = _createElementVNode("span", null, "服务状态", -1)),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_btn, {
                        icon: "",
                        size: "small",
                        onClick: refreshStatus,
                        loading: refreshing.value
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_icon, null, {
                            default: _withCtx(() => _cache[10] || (_cache[10] = [
                              _createTextVNode("mdi-refresh")
                            ])),
                            _: 1,
                            __: [10]
                          })
                        ]),
                        _: 1
                      }, 8, ["loading"])
                    ]),
                    _: 1,
                    __: [11]
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_1, [
                        _cache[12] || (_cache[12] = _createElementVNode("span", { class: "label font-weight-bold" }, "运行状态：", -1)),
                        _createVNode(_component_v_chip, {
                          color: status.server_status === 'running' ? 'success' : 'grey',
                          size: "small",
                          class: "ml-1",
                          variant: "elevated"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(status.server_status === 'running' ? '已启用' : '已禁用'), 1)
                          ]),
                          _: 1
                        }, 8, ["color"])
                      ]),
                      _createElementVNode("div", _hoisted_2, [
                        _cache[13] || (_cache[13] = _createElementVNode("span", { class: "label font-weight-bold" }, "服务端口：", -1)),
                        _createVNode(_component_v_chip, {
                          color: "primary",
                          size: "small",
                          class: "ml-1",
                          variant: "elevated"
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(status.port || '未配置'), 1)
                          ]),
                          _: 1
                        })
                      ]),
                      _createElementVNode("div", _hoisted_3, [
                        _cache[14] || (_cache[14] = _createElementVNode("span", { class: "label font-weight-bold" }, "服务监听IP：", -1)),
                        _createVNode(_component_v_chip, {
                          color: "info",
                          size: "small",
                          class: "ml-1",
                          variant: "elevated"
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
          _createVNode(_component_v_col, {
            cols: "12",
            md: "3"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card, {
                class: "glass-card",
                elevation: "4"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        color: "info",
                        size: "24",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => _cache[15] || (_cache[15] = [
                          _createTextVNode("mdi-folder-check")
                        ])),
                        _: 1,
                        __: [15]
                      }),
                      _cache[16] || (_cache[16] = _createElementVNode("span", null, "目录监控", -1))
                    ]),
                    _: 1,
                    __: [16]
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_4, [
                        _cache[17] || (_cache[17] = _createElementVNode("span", { class: "label" }, "横屏目录：", -1)),
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
                      _createElementVNode("div", _hoisted_5, [
                        _cache[18] || (_cache[18] = _createElementVNode("span", { class: "label" }, "竖屏目录：", -1)),
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
                      _createElementVNode("div", _hoisted_6, [
                        _cache[19] || (_cache[19] = _createElementVNode("span", { class: "label" }, "配置完整性：", -1)),
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
          _createVNode(_component_v_col, {
            cols: "12",
            md: "3"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card, {
                class: "glass-card",
                elevation: "4"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        color: "info",
                        size: "24",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => _cache[20] || (_cache[20] = [
                          _createTextVNode("mdi-image")
                        ])),
                        _: 1,
                        __: [20]
                      }),
                      _cache[21] || (_cache[21] = _createElementVNode("span", null, "图片统计", -1))
                    ]),
                    _: 1,
                    __: [21]
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_7, [
                        _createElementVNode("div", _hoisted_8, [
                          _createElementVNode("div", _hoisted_9, [
                            (!status.pc_path && status.network_image_url_pc || !status.mobile_path && status.network_image_url_mobile)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_10, "未知"))
                              : (_openBlock(), _createElementBlock("span", _hoisted_11, _toDisplayString(status.total_count), 1))
                          ]),
                          _cache[22] || (_cache[22] = _createElementVNode("div", { class: "stat-label" }, "总图片数", -1))
                        ]),
                        _createElementVNode("div", _hoisted_12, [
                          _createElementVNode("div", _hoisted_13, [
                            (!status.pc_path && status.network_image_url_pc)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_14, "未知"))
                              : (_openBlock(), _createElementBlock("span", _hoisted_15, _toDisplayString(status.pc_count), 1))
                          ]),
                          _cache[23] || (_cache[23] = _createElementVNode("div", { class: "stat-label" }, "横屏图片", -1))
                        ]),
                        _createElementVNode("div", _hoisted_16, [
                          _createElementVNode("div", _hoisted_17, [
                            (!status.mobile_path && status.network_image_url_mobile)
                              ? (_openBlock(), _createElementBlock("span", _hoisted_18, "未知"))
                              : (_openBlock(), _createElementBlock("span", _hoisted_19, _toDisplayString(status.mobile_count), 1))
                          ]),
                          _cache[24] || (_cache[24] = _createElementVNode("div", { class: "stat-label" }, "竖屏图片", -1))
                        ]),
                        _createElementVNode("div", _hoisted_20, [
                          _createElementVNode("div", _hoisted_21, _toDisplayString(status.today_visits), 1),
                          _cache[25] || (_cache[25] = _createElementVNode("div", { class: "stat-label" }, "今日访问", -1))
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
          }),
          _createVNode(_component_v_col, {
            cols: "12",
            md: "3"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_v_card, {
                class: "glass-card",
                elevation: "4"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_v_card_title, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_icon, {
                        color: "primary",
                        size: "24",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => _cache[26] || (_cache[26] = [
                          _createTextVNode("mdi-lightning-bolt")
                        ])),
                        _: 1,
                        __: [26]
                      }),
                      _cache[27] || (_cache[27] = _createElementVNode("span", null, "快速操作", -1))
                    ]),
                    _: 1,
                    __: [27]
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_22, [
                        _createVNode(_component_v_btn, {
                          color: "info",
                          size: "small",
                          "prepend-icon": "mdi-cog",
                          onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('switch'))),
                          class: "action-btn"
                        }, {
                          default: _withCtx(() => _cache[28] || (_cache[28] = [
                            _createTextVNode(" 插件配置 ")
                          ])),
                          _: 1,
                          __: [28]
                        }),
                        _createVNode(_component_v_btn, {
                          color: "warning",
                          size: "small",
                          "prepend-icon": "mdi-restart",
                          onClick: startService,
                          loading: starting.value,
                          class: "action-btn"
                        }, {
                          default: _withCtx(() => _cache[29] || (_cache[29] = [
                            _createTextVNode(" 重启服务 ")
                          ])),
                          _: 1,
                          __: [29]
                        }, 8, ["loading"])
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
      }),
      _createVNode(_component_v_row, { class: "mb-6" }, {
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
                        color: "primary",
                        size: "24",
                        class: "mr-2"
                      }, {
                        default: _withCtx(() => _cache[30] || (_cache[30] = [
                          _createTextVNode("mdi-image-search")
                        ])),
                        _: 1,
                        __: [30]
                      }),
                      _cache[35] || (_cache[35] = _createElementVNode("span", null, "图片预览", -1)),
                      _createVNode(_component_v_spacer),
                      _createVNode(_component_v_btn_group, null, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_btn, {
                            size: "small",
                            color: previewType.value === 'pc' ? 'primary' : 'grey',
                            onClick: _cache[2] || (_cache[2] = $event => (previewType.value = 'pc'))
                          }, {
                            default: _withCtx(() => _cache[31] || (_cache[31] = [
                              _createTextVNode(" 横屏 ")
                            ])),
                            _: 1,
                            __: [31]
                          }, 8, ["color"]),
                          _createVNode(_component_v_btn, {
                            size: "small",
                            color: previewType.value === 'mobile' ? 'primary' : 'grey',
                            onClick: _cache[3] || (_cache[3] = $event => (previewType.value = 'mobile'))
                          }, {
                            default: _withCtx(() => _cache[32] || (_cache[32] = [
                              _createTextVNode(" 竖屏 ")
                            ])),
                            _: 1,
                            __: [32]
                          }, 8, ["color"]),
                          _createVNode(_component_v_btn, {
                            size: "small",
                            color: previewType.value === 'auto' ? 'primary' : 'grey',
                            onClick: _cache[4] || (_cache[4] = $event => (previewType.value = 'auto'))
                          }, {
                            default: _withCtx(() => _cache[33] || (_cache[33] = [
                              _createTextVNode(" 自动 ")
                            ])),
                            _: 1,
                            __: [33]
                          }, 8, ["color"])
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_v_btn, {
                        color: "primary",
                        size: "small",
                        class: "ml-4 btn-gradient-refresh",
                        "prepend-icon": "mdi-refresh",
                        onClick: loadPreview,
                        loading: previewLoading.value
                      }, {
                        default: _withCtx(() => _cache[34] || (_cache[34] = [
                          _createTextVNode(" 刷新预览 ")
                        ])),
                        _: 1,
                        __: [34]
                      }, 8, ["loading"])
                    ]),
                    _: 1,
                    __: [35]
                  }),
                  _createVNode(_component_v_card_text, null, {
                    default: _withCtx(() => [
                      _createElementVNode("div", _hoisted_23, [
                        (previewLoading.value && !previewImageUrl.value)
                          ? (_openBlock(), _createElementBlock("div", _hoisted_24, [
                              _createVNode(_component_v_progress_circular, {
                                indeterminate: "",
                                color: "primary",
                                size: "64"
                              }),
                              _cache[36] || (_cache[36] = _createElementVNode("div", { class: "mt-4" }, "正在加载图片...", -1))
                            ]))
                          : (previewError.value)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_25, [
                                _createVNode(_component_v_icon, {
                                  color: "error",
                                  size: "64"
                                }, {
                                  default: _withCtx(() => _cache[37] || (_cache[37] = [
                                    _createTextVNode("mdi-image-broken")
                                  ])),
                                  _: 1,
                                  __: [37]
                                }),
                                _createElementVNode("div", _hoisted_26, _toDisplayString(previewError.value), 1),
                                _createVNode(_component_v_btn, {
                                  color: "primary",
                                  onClick: loadPreview,
                                  class: "mt-4"
                                }, {
                                  default: _withCtx(() => _cache[38] || (_cache[38] = [
                                    _createTextVNode("重试")
                                  ])),
                                  _: 1,
                                  __: [38]
                                })
                              ]))
                            : (_openBlock(), _createElementBlock("div", _hoisted_27, [
                                (previewImageUrl.value)
                                  ? (_openBlock(), _createElementBlock("img", {
                                      key: 0,
                                      src: previewImageUrl.value,
                                      alt: '随机图片预览 - ' + previewType.value,
                                      class: "preview-image",
                                      onLoad: _cache[5] || (_cache[5] = $event => (previewLoading.value = false)),
                                      onError: handlePreviewError
                                    }, null, 40, _hoisted_28))
                                  : (_openBlock(), _createElementBlock("div", _hoisted_29, [
                                      _createVNode(_component_v_icon, {
                                        color: "grey",
                                        size: "64"
                                      }, {
                                        default: _withCtx(() => _cache[39] || (_cache[39] = [
                                          _createTextVNode("mdi-image")
                                        ])),
                                        _: 1,
                                        __: [39]
                                      }),
                                      _cache[40] || (_cache[40] = _createElementVNode("div", { class: "mt-4 text-grey" }, "点击下方按钮预览图片", -1))
                                    ]))
                              ]))
                      ])
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_v_card_actions, { class: "preview-actions" })
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
                        default: _withCtx(() => _cache[41] || (_cache[41] = [
                          _createTextVNode("mdi-api")
                        ])),
                        _: 1,
                        __: [41]
                      }),
                      _cache[42] || (_cache[42] = _createElementVNode("span", null, "API 接口", -1))
                    ]),
                    _: 1,
                    __: [42]
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
                                  _createVNode(_component_v_icon, {
                                    color: "primary",
                                    size: "20",
                                    class: "mr-2"
                                  }, {
                                    default: _withCtx(() => _cache[43] || (_cache[43] = [
                                      _createTextVNode("mdi-web")
                                    ])),
                                    _: 1,
                                    __: [43]
                                  }),
                                  _cache[44] || (_cache[44] = _createElementVNode("span", { class: "api-title" }, "自动识别设备", -1))
                                ]),
                                _createElementVNode("div", _hoisted_32, _toDisplayString(getApiUrl('/random')), 1),
                                _cache[45] || (_cache[45] = _createElementVNode("div", { class: "endpoint-desc" }, "根据设备类型自动返回横屏或竖屏图片", -1))
                              ])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_33, [
                                _createElementVNode("div", _hoisted_34, [
                                  _createVNode(_component_v_icon, {
                                    color: "success",
                                    size: "20",
                                    class: "mr-2"
                                  }, {
                                    default: _withCtx(() => _cache[46] || (_cache[46] = [
                                      _createTextVNode("mdi-monitor")
                                    ])),
                                    _: 1,
                                    __: [46]
                                  }),
                                  _cache[47] || (_cache[47] = _createElementVNode("span", { class: "api-title" }, "指定横屏图片", -1))
                                ]),
                                _createElementVNode("div", _hoisted_35, _toDisplayString(getApiUrl('/random?type=pc')), 1),
                                _cache[48] || (_cache[48] = _createElementVNode("div", { class: "endpoint-desc" }, "强制返回横屏图片", -1))
                              ])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_36, [
                                _createElementVNode("div", _hoisted_37, [
                                  _createVNode(_component_v_icon, {
                                    color: "warning",
                                    size: "20",
                                    class: "mr-2"
                                  }, {
                                    default: _withCtx(() => _cache[49] || (_cache[49] = [
                                      _createTextVNode("mdi-cellphone")
                                    ])),
                                    _: 1,
                                    __: [49]
                                  }),
                                  _cache[50] || (_cache[50] = _createElementVNode("span", { class: "api-title" }, "指定竖屏图片", -1))
                                ]),
                                _createElementVNode("div", _hoisted_38, _toDisplayString(getApiUrl('/random?type=mobile')), 1),
                                _cache[51] || (_cache[51] = _createElementVNode("div", { class: "endpoint-desc" }, "强制返回竖屏图片", -1))
                              ])
                            ]),
                            _: 1
                          }),
                          _createVNode(_component_v_col, {
                            cols: "12",
                            md: "3"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_39, [
                                _createElementVNode("div", _hoisted_40, [
                                  _createVNode(_component_v_icon, {
                                    color: "info",
                                    size: "20",
                                    class: "mr-2"
                                  }, {
                                    default: _withCtx(() => _cache[52] || (_cache[52] = [
                                      _createTextVNode("mdi-chart-bar")
                                    ])),
                                    _: 1,
                                    __: [52]
                                  }),
                                  _cache[53] || (_cache[53] = _createElementVNode("span", { class: "api-title" }, "统计数据", -1))
                                ]),
                                _createElementVNode("div", _hoisted_41, _toDisplayString(getApiUrl('/stats')), 1),
                                _cache[54] || (_cache[54] = _createElementVNode("div", { class: "endpoint-desc" }, "获取图片数量和访问统计", -1))
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
      _createVNode(_component_v_snackbar, {
        modelValue: snackbar.show,
        "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((snackbar.show) = $event)),
        color: snackbar.color,
        timeout: snackbar.timeout
      }, {
        default: _withCtx(() => [
          _createTextVNode(_toDisplayString(snackbar.text), 1)
        ]),
        _: 1
      }, 8, ["modelValue", "color", "timeout"])
    ]),
    _: 1
  }))
}
}

};
const PageComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-893caf23"]]);

export { PageComponent as default };
