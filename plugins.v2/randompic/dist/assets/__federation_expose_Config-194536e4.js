import { importShared } from './__federation_fn_import-a2e11483.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_3cf49a33_lang = '';

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,createElementVNode:_createElementVNode,vModelCheckbox:_vModelCheckbox,withDirectives:_withDirectives,openBlock:_openBlock,toDisplayString:_toDisplayString,createBlock:_createBlock,createCommentVNode:_createCommentVNode,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };
const _hoisted_2 = { class: "config-wrapper" };
const _hoisted_3 = { class: "title-bar" };
const _hoisted_4 = { class: "title-left" };
const _hoisted_5 = { class: "title-right" };
const _hoisted_6 = { class: "title-actions" };
const _hoisted_7 = { class: "config-body" };
const _hoisted_8 = { class: "mp-card config-section basic-settings" };
const _hoisted_9 = { class: "section-title" };
const _hoisted_10 = { class: "card-inner" };
const _hoisted_11 = { class: "config-switch-row" };
const _hoisted_12 = { class: "switch" };
const _hoisted_13 = {
  class: "port-hint",
  style: {"font-size":"12px","display":"flex","align-items":"center","margin-top":"8px","margin-bottom":"0"}
};
const _hoisted_14 = { class: "mp-card config-section local-directory-settings" };
const _hoisted_15 = { class: "section-title" };
const _hoisted_16 = { class: "card-inner" };
const _hoisted_17 = { class: "directory-card pc-directory" };
const _hoisted_18 = { class: "directory-header" };
const _hoisted_19 = { class: "directory-card mobile-directory" };
const _hoisted_20 = { class: "directory-header" };
const _hoisted_21 = { class: "mp-card config-section network-directory-settings" };
const _hoisted_22 = { class: "section-title" };
const _hoisted_23 = { class: "card-inner" };
const _hoisted_24 = { class: "directory-card pc-directory" };
const _hoisted_25 = { class: "directory-header" };
const _hoisted_26 = { class: "directory-card mobile-directory" };
const _hoisted_27 = { class: "directory-header" };

const {ref,reactive,onMounted,computed} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) }
},
  emits: ['close', 'switch', 'config-updated-on-server', 'back-to-status'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

// 响应式数据
const config = reactive({
  enable: false,
  port: "8002",
  pc_path: "",
  mobile_path: "",
  network_image_url_pc: "",
  network_image_url_mobile: "",
  network_image_url: "", // 兼容老配置
});

const saving = ref(false);
const imageRotation = ref(0);

const successMessage = ref(null);
const errorMessage = ref(null);

const isConfigValid = () => {
  const hasPc = config.pc_path || config.network_image_url_pc;
  const hasMobile = config.mobile_path || config.network_image_url_mobile;
  return config.port && hasPc && hasMobile;
};

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


const onConfigChange = () => {
  // 配置变更时的处理
};

const resetConfig = () => {
  Object.assign(config, {
    enable: false,
    port: "8002",
    pc_path: "",
    mobile_path: "",
    network_image_url_pc: "",
    network_image_url_mobile: "",
    network_image_url: "",
  });
  showNotification('配置已重置', 'success');
};

const saveConfig = async () => {
  if (!isConfigValid()) {
    showNotification('请完善配置信息', 'error');
    return;
  }

  saving.value = true;
  try {
    const result = await props.api.post('plugin/RandomPic/config', config);
    showNotification('配置保存成功', 'success');
    emit('save', JSON.parse(JSON.stringify(config)));
    emit('config-updated-on-server', config);
  } catch (error) {
    showNotification('配置保存失败', 'error');
  } finally {
    saving.value = false;
  }
};

// 生命周期
onMounted(() => {
  // 初始化配置
  if (props.initialConfig) {
    Object.assign(config, props.initialConfig);
  }

  // 启动图片旋转动画
  setInterval(() => {
    imageRotation.value = (imageRotation.value + 1) % 360;
  }, 50);
});

return (_ctx, _cache) => {
  const _component_v_icon = _resolveComponent("v-icon");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_alert = _resolveComponent("v-alert");
  const _component_v_card = _resolveComponent("v-card");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_v_card, {
      flat: "",
      class: "rounded border"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_v_card_text, null, {
          default: _withCtx(() => [
            _createElementVNode("div", _hoisted_2, [
              _createElementVNode("div", _hoisted_3, [
                _createElementVNode("div", _hoisted_4, [
                  _createVNode(_component_v_icon, {
                    size: "28",
                    color: "primary",
                    class: "mr-2"
                  }, {
                    default: _withCtx(() => _cache[8] || (_cache[8] = [
                      _createTextVNode("mdi-cog")
                    ])),
                    _: 1,
                    __: [8]
                  }),
                  _cache[9] || (_cache[9] = _createElementVNode("div", { class: "title-texts" }, [
                    _createElementVNode("div", { class: "title-main" }, "图床配置"),
                    _createElementVNode("div", { class: "title-sub" }, "配置您的随机图片服务")
                  ], -1))
                ]),
                _createElementVNode("div", _hoisted_5, [
                  _createElementVNode("div", _hoisted_6, [
                    _createVNode(_component_v_btn, {
                      class: "btn-gradient-status",
                      onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('switch'))),
                      disabled: saving.value,
                      size: "small"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, { class: "btn-icon" }, {
                          default: _withCtx(() => _cache[10] || (_cache[10] = [
                            _createTextVNode("mdi-view-dashboard")
                          ])),
                          _: 1,
                          __: [10]
                        }),
                        _cache[11] || (_cache[11] = _createElementVNode("span", { class: "btn-text" }, "状态页", -1))
                      ]),
                      _: 1,
                      __: [11]
                    }, 8, ["disabled"]),
                    _createVNode(_component_v_btn, {
                      class: "btn-gradient-reset",
                      onClick: resetConfig,
                      disabled: saving.value,
                      size: "small"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, { class: "btn-icon" }, {
                          default: _withCtx(() => _cache[12] || (_cache[12] = [
                            _createTextVNode("mdi-restore")
                          ])),
                          _: 1,
                          __: [12]
                        }),
                        _cache[13] || (_cache[13] = _createElementVNode("span", { class: "btn-text" }, "重置", -1))
                      ]),
                      _: 1,
                      __: [13]
                    }, 8, ["disabled"]),
                    _createVNode(_component_v_btn, {
                      class: "btn-gradient-save",
                      disabled: !isConfigValid() || saving.value,
                      onClick: saveConfig,
                      loading: saving.value,
                      size: "small"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, { class: "btn-icon" }, {
                          default: _withCtx(() => _cache[14] || (_cache[14] = [
                            _createTextVNode("mdi-content-save")
                          ])),
                          _: 1,
                          __: [14]
                        }),
                        _cache[15] || (_cache[15] = _createElementVNode("span", { class: "btn-text" }, "保存配置", -1))
                      ]),
                      _: 1,
                      __: [15]
                    }, 8, ["disabled", "loading"]),
                    _createVNode(_component_v_btn, {
                      class: "btn-gradient-close",
                      onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('close'))),
                      disabled: saving.value,
                      size: "small"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_icon, { class: "btn-icon" }, {
                          default: _withCtx(() => _cache[16] || (_cache[16] = [
                            _createTextVNode("mdi-close")
                          ])),
                          _: 1,
                          __: [16]
                        }),
                        _cache[17] || (_cache[17] = _createElementVNode("span", { class: "btn-text" }, "关闭", -1))
                      ]),
                      _: 1,
                      __: [17]
                    }, 8, ["disabled"])
                  ])
                ])
              ]),
              _createElementVNode("div", _hoisted_7, [
                _createElementVNode("div", _hoisted_8, [
                  _cache[25] || (_cache[25] = _createElementVNode("div", { class: "card-overlay" }, null, -1)),
                  _createElementVNode("div", _hoisted_9, [
                    _createVNode(_component_v_icon, {
                      class: "mr-2",
                      color: "primary"
                    }, {
                      default: _withCtx(() => _cache[18] || (_cache[18] = [
                        _createTextVNode("mdi-tune")
                      ])),
                      _: 1,
                      __: [18]
                    }),
                    _cache[19] || (_cache[19] = _createTextVNode(" 基本设置 "))
                  ]),
                  _createElementVNode("div", _hoisted_10, [
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, { dense: "" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_11, [
                                  _createVNode(_component_v_icon, {
                                    size: "18",
                                    class: "switch-icon",
                                    color: config.enable ? 'success' : 'grey'
                                  }, {
                                    default: _withCtx(() => _cache[20] || (_cache[20] = [
                                      _createTextVNode("mdi-power")
                                    ])),
                                    _: 1,
                                    __: [20]
                                  }, 8, ["color"]),
                                  _cache[22] || (_cache[22] = _createElementVNode("span", { class: "switch-label" }, "启用插件", -1)),
                                  _createElementVNode("label", _hoisted_12, [
                                    _withDirectives(_createElementVNode("input", {
                                      type: "checkbox",
                                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.enable) = $event)),
                                      onChange: onConfigChange
                                    }, null, 544), [
                                      [_vModelCheckbox, config.enable]
                                    ]),
                                    _cache[21] || (_cache[21] = _createElementVNode("div", { class: "slider" }, [
                                      _createElementVNode("div", { class: "circle" }, [
                                        _createElementVNode("svg", {
                                          class: "cross",
                                          viewBox: "0 0 365.696 365.696",
                                          height: "6",
                                          width: "6",
                                          xmlns: "http://www.w3.org/2000/svg"
                                        }, [
                                          _createElementVNode("path", {
                                            fill: "currentColor",
                                            d: "M243.188 182.86 356.32 69.726c12.5-12.5 12.5-32.766 0-45.247L341.238 9.398c-12.504-12.503-32.77-12.503-45.25 0L182.86 122.528 69.727 9.374c-12.5-12.5-32.766-12.5-45.247 0L9.375 24.457c-12.5 12.504-12.5 32.77 0 45.25l113.152 113.152L9.398 295.99c-12.503 12.503-12.503 32.769 0 45.25L24.48 356.32c12.5 12.5 32.766 12.5 45.247 0l113.132-113.132L295.99 356.32c12.503 12.5 32.769 12.5 45.25 0l15.081-15.082c12.5-12.504 12.5-32.77 0-45.25zm0 0"
                                          })
                                        ]),
                                        _createElementVNode("svg", {
                                          class: "checkmark",
                                          viewBox: "0 0 24 24",
                                          height: "10",
                                          width: "10",
                                          xmlns: "http://www.w3.org/2000/svg"
                                        }, [
                                          _createElementVNode("path", {
                                            fill: "currentColor",
                                            d: "M9.707 19.121a.997.997 0 0 1-1.414 0l-5.646-5.647a1.5 1.5 0 0 1 0-2.121l.707-.707a1.5 1.5 0 0 1 2.121 0L9 14.171l9.525-9.525a1.5 1.5 0 0 1 2.121 0l.707.707a1.5 1.5 0 0 1 0 2.121z"
                                          })
                                        ])
                                      ])
                                    ], -1))
                                  ])
                                ])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_v_col, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_v_text_field, {
                                  modelValue: config.port,
                                  "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.port) = $event)),
                                  label: "服务端口",
                                  placeholder: "8002",
                                  "prepend-inner-icon": "mdi-numeric",
                                  hint: "",
                                  dense: "",
                                  onInput: onConfigChange
                                }, null, 8, ["modelValue"]),
                                _createElementVNode("div", _hoisted_13, [
                                  _createVNode(_component_v_icon, {
                                    size: "16",
                                    color: "info",
                                    style: {"margin-right":"4px"}
                                  }, {
                                    default: _withCtx(() => _cache[23] || (_cache[23] = [
                                      _createTextVNode("mdi-information")
                                    ])),
                                    _: 1,
                                    __: [23]
                                  }),
                                  _cache[24] || (_cache[24] = _createTextVNode(" 容器为 bridge 模式需要手动映射配置的端口 "))
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
                  ])
                ]),
                _createElementVNode("div", _hoisted_14, [
                  _cache[34] || (_cache[34] = _createElementVNode("div", { class: "card-overlay" }, null, -1)),
                  _createElementVNode("div", _hoisted_15, [
                    _createVNode(_component_v_icon, {
                      class: "mr-2",
                      color: "info"
                    }, {
                      default: _withCtx(() => _cache[26] || (_cache[26] = [
                        _createTextVNode("mdi-folder-multiple-image")
                      ])),
                      _: 1,
                      __: [26]
                    }),
                    _cache[27] || (_cache[27] = _createTextVNode(" 本地目录配置 "))
                  ]),
                  _createElementVNode("div", _hoisted_16, [
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, {
                          dense: "",
                          class: "mb-4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_17, [
                                  _createElementVNode("div", _hoisted_18, [
                                    _createVNode(_component_v_icon, {
                                      color: "primary",
                                      size: "24",
                                      class: "mr-2"
                                    }, {
                                      default: _withCtx(() => _cache[28] || (_cache[28] = [
                                        _createTextVNode("mdi-monitor")
                                      ])),
                                      _: 1,
                                      __: [28]
                                    }),
                                    _cache[30] || (_cache[30] = _createElementVNode("span", { class: "directory-title" }, "横屏本地图片目录", -1)),
                                    _createVNode(_component_v_chip, {
                                      color: "primary",
                                      size: "small",
                                      class: "ml-2"
                                    }, {
                                      default: _withCtx(() => _cache[29] || (_cache[29] = [
                                        _createTextVNode("PC/横屏")
                                      ])),
                                      _: 1,
                                      __: [29]
                                    })
                                  ]),
                                  _createVNode(_component_v_text_field, {
                                    modelValue: config.pc_path,
                                    "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.pc_path) = $event)),
                                    label: "横屏图片路径",
                                    placeholder: "/path/pc/images",
                                    "prepend-inner-icon": "mdi-folder",
                                    hint: "",
                                    dense: "",
                                    onInput: onConfigChange
                                  }, null, 8, ["modelValue"])
                                ])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_row, { dense: "" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_19, [
                                  _createElementVNode("div", _hoisted_20, [
                                    _createVNode(_component_v_icon, {
                                      color: "success",
                                      size: "24",
                                      class: "mr-2"
                                    }, {
                                      default: _withCtx(() => _cache[31] || (_cache[31] = [
                                        _createTextVNode("mdi-cellphone")
                                      ])),
                                      _: 1,
                                      __: [31]
                                    }),
                                    _cache[33] || (_cache[33] = _createElementVNode("span", { class: "directory-title" }, "竖屏本地图片目录", -1)),
                                    _createVNode(_component_v_chip, {
                                      color: "success",
                                      size: "small",
                                      class: "ml-2"
                                    }, {
                                      default: _withCtx(() => _cache[32] || (_cache[32] = [
                                        _createTextVNode("Mobile/竖屏")
                                      ])),
                                      _: 1,
                                      __: [32]
                                    })
                                  ]),
                                  _createVNode(_component_v_text_field, {
                                    modelValue: config.mobile_path,
                                    "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.mobile_path) = $event)),
                                    label: "竖屏图片路径",
                                    placeholder: "/path/mobile/images",
                                    "prepend-inner-icon": "mdi-folder",
                                    hint: "",
                                    dense: "",
                                    onInput: onConfigChange
                                  }, null, 8, ["modelValue"])
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
                  ])
                ]),
                _createElementVNode("div", _hoisted_21, [
                  _cache[43] || (_cache[43] = _createElementVNode("div", { class: "card-overlay" }, null, -1)),
                  _createElementVNode("div", _hoisted_22, [
                    _createVNode(_component_v_icon, {
                      class: "mr-2",
                      color: "primary"
                    }, {
                      default: _withCtx(() => _cache[35] || (_cache[35] = [
                        _createTextVNode("mdi-link-variant")
                      ])),
                      _: 1,
                      __: [35]
                    }),
                    _cache[36] || (_cache[36] = _createTextVNode(" 网络目录配置 "))
                  ]),
                  _createElementVNode("div", _hoisted_23, [
                    _createVNode(_component_v_card_text, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_v_row, {
                          dense: "",
                          class: "mb-4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_24, [
                                  _createElementVNode("div", _hoisted_25, [
                                    _createVNode(_component_v_icon, {
                                      color: "primary",
                                      size: "24",
                                      class: "mr-2"
                                    }, {
                                      default: _withCtx(() => _cache[37] || (_cache[37] = [
                                        _createTextVNode("mdi-monitor")
                                      ])),
                                      _: 1,
                                      __: [37]
                                    }),
                                    _cache[39] || (_cache[39] = _createElementVNode("span", { class: "directory-title" }, "横屏网络图片地址", -1)),
                                    _createVNode(_component_v_chip, {
                                      color: "primary",
                                      size: "small",
                                      class: "ml-2"
                                    }, {
                                      default: _withCtx(() => _cache[38] || (_cache[38] = [
                                        _createTextVNode("PC/横屏")
                                      ])),
                                      _: 1,
                                      __: [38]
                                    })
                                  ]),
                                  _createVNode(_component_v_text_field, {
                                    modelValue: config.network_image_url_pc,
                                    "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((config.network_image_url_pc) = $event)),
                                    label: "横屏网络图片地址",
                                    placeholder: "https://example.com/your-pc-image.jpg，支持多个逗号分隔",
                                    "prepend-inner-icon": "mdi-link",
                                    hint: "支持图片直链、API、json/txt等，多个用英文逗号分隔，优先级高于本地横屏目录",
                                    "persistent-hint": "",
                                    dense: "",
                                    onInput: onConfigChange
                                  }, null, 8, ["modelValue"])
                                ])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_v_row, { dense: "" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_v_col, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_26, [
                                  _createElementVNode("div", _hoisted_27, [
                                    _createVNode(_component_v_icon, {
                                      color: "success",
                                      size: "24",
                                      class: "mr-2"
                                    }, {
                                      default: _withCtx(() => _cache[40] || (_cache[40] = [
                                        _createTextVNode("mdi-cellphone-link")
                                      ])),
                                      _: 1,
                                      __: [40]
                                    }),
                                    _cache[42] || (_cache[42] = _createElementVNode("span", { class: "directory-title" }, "竖屏网络图片地址", -1)),
                                    _createVNode(_component_v_chip, {
                                      color: "success",
                                      size: "small",
                                      class: "ml-2"
                                    }, {
                                      default: _withCtx(() => _cache[41] || (_cache[41] = [
                                        _createTextVNode("Mobile/竖屏")
                                      ])),
                                      _: 1,
                                      __: [41]
                                    })
                                  ]),
                                  _createVNode(_component_v_text_field, {
                                    modelValue: config.network_image_url_mobile,
                                    "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((config.network_image_url_mobile) = $event)),
                                    label: "竖屏网络图片地址",
                                    placeholder: "https://example.com/your-mobile-image.jpg，支持多个逗号分隔",
                                    "prepend-inner-icon": "mdi-link",
                                    hint: "支持图片直链、API、json/txt等，多个用英文逗号分隔，优先级高于本地竖屏目录",
                                    "persistent-hint": "",
                                    dense: "",
                                    onInput: onConfigChange
                                  }, null, 8, ["modelValue"])
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
                  ])
                ])
              ])
            ]),
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
        })
      ]),
      _: 1
    })
  ]))
}
}

};
const ConfigComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-3cf49a33"]]);

export { ConfigComponent as default };
