import { importShared } from './__federation_fn_import-a2e11483.js';
import { _ as _export_sfc } from './_plugin-vue_export-helper-c4c0bc37.js';

const Config_vue_vue_type_style_index_0_scoped_cdf50601_lang = '';

const {createTextVNode:_createTextVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,createVNode:_createVNode,normalizeStyle:_normalizeStyle,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,openBlock:_openBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "plugin-config" };
const _hoisted_2 = { class: "config-header" };
const _hoisted_3 = { class: "gallery-visual" };
const _hoisted_4 = { class: "floating-images" };
const _hoisted_5 = { class: "config-title" };
const _hoisted_6 = { class: "glass-card config-section basic-settings" };
const _hoisted_7 = { class: "section-title" };
const _hoisted_8 = {
  class: "port-hint",
  style: {"font-size":"12px","display":"flex","align-items":"center","margin-top":"8px","margin-bottom":"0"}
};
const _hoisted_9 = { class: "glass-card config-section local-directory-settings" };
const _hoisted_10 = { class: "section-title" };
const _hoisted_11 = { class: "directory-card pc-directory" };
const _hoisted_12 = { class: "directory-header" };
const _hoisted_13 = { class: "directory-card mobile-directory" };
const _hoisted_14 = { class: "directory-header" };
const _hoisted_15 = { class: "glass-card config-section network-directory-settings" };
const _hoisted_16 = { class: "section-title" };
const _hoisted_17 = { class: "directory-card pc-directory" };
const _hoisted_18 = { class: "directory-header" };
const _hoisted_19 = { class: "directory-card mobile-directory" };
const _hoisted_20 = { class: "directory-header" };

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

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
  timeout: 3000
});

const isConfigValid = () => {
  const hasPc = config.pc_path || config.network_image_url_pc;
  const hasMobile = config.mobile_path || config.network_image_url_mobile;
  return config.port && hasPc && hasMobile;
};

// 方法
const showNotification = (text, color = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
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
  showNotification('配置已重置', 'info');
};

const saveConfig = async () => {
  if (!isConfigValid()) {
    showNotification('请完善配置信息', 'warning');
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
  const _component_v_switch = _resolveComponent("v-switch");
  const _component_v_col = _resolveComponent("v-col");
  const _component_v_text_field = _resolveComponent("v-text-field");
  const _component_v_row = _resolveComponent("v-row");
  const _component_v_card_text = _resolveComponent("v-card-text");
  const _component_v_chip = _resolveComponent("v-chip");
  const _component_v_snackbar = _resolveComponent("v-snackbar");
  const _component_v_btn = _resolveComponent("v-btn");
  const _component_v_spacer = _resolveComponent("v-spacer");
  const _component_v_card_actions = _resolveComponent("v-card-actions");
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
                  _createElementVNode("div", {
                    class: "floating-image img-1",
                    style: _normalizeStyle({ transform: `rotate(${imageRotation.value}deg)` })
                  }, [
                    _createVNode(_component_v_icon, {
                      size: "32",
                      color: "primary"
                    }, {
                      default: _withCtx(() => _cache[9] || (_cache[9] = [
                        _createTextVNode("mdi-image")
                      ])),
                      _: 1,
                      __: [9]
                    })
                  ], 4),
                  _createElementVNode("div", {
                    class: "floating-image img-2",
                    style: _normalizeStyle({ transform: `rotate(${-imageRotation.value}deg)` })
                  }, [
                    _createVNode(_component_v_icon, {
                      size: "28",
                      color: "success"
                    }, {
                      default: _withCtx(() => _cache[10] || (_cache[10] = [
                        _createTextVNode("mdi-image-multiple")
                      ])),
                      _: 1,
                      __: [10]
                    })
                  ], 4),
                  _createElementVNode("div", {
                    class: "floating-image img-3",
                    style: _normalizeStyle({ transform: `rotate(${imageRotation.value * 0.5}deg)` })
                  }, [
                    _createVNode(_component_v_icon, {
                      size: "24",
                      color: "warning"
                    }, {
                      default: _withCtx(() => _cache[11] || (_cache[11] = [
                        _createTextVNode("mdi-image-outline")
                      ])),
                      _: 1,
                      __: [11]
                    })
                  ], 4)
                ]),
                _createElementVNode("div", _hoisted_5, [
                  _createVNode(_component_v_icon, {
                    size: "36",
                    color: "primary",
                    class: "mr-3"
                  }, {
                    default: _withCtx(() => _cache[12] || (_cache[12] = [
                      _createTextVNode("mdi-cog")
                    ])),
                    _: 1,
                    __: [12]
                  }),
                  _cache[13] || (_cache[13] = _createElementVNode("span", { class: "text-h4 font-weight-bold" }, "图库配置", -1))
                ]),
                _cache[14] || (_cache[14] = _createElementVNode("div", { class: "config-subtitle" }, "配置您的随机图片服务", -1))
              ])
            ]),
            _createElementVNode("div", _hoisted_6, [
              _createElementVNode("div", _hoisted_7, [
                _createVNode(_component_v_icon, {
                  class: "mr-2",
                  color: "primary"
                }, {
                  default: _withCtx(() => _cache[15] || (_cache[15] = [
                    _createTextVNode("mdi-tune")
                  ])),
                  _: 1,
                  __: [15]
                }),
                _cache[16] || (_cache[16] = _createTextVNode(" 基本设置 "))
              ]),
              _createVNode(_component_v_card_text, null, {
                default: _withCtx(() => [
                  _createVNode(_component_v_row, { dense: "" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_col, {
                        cols: "12",
                        md: "6"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_v_switch, {
                            modelValue: config.enable,
                            "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((config.enable) = $event)),
                            label: "启用插件",
                            color: "success",
                            "prepend-icon": "mdi-power",
                            class: "config-switch",
                            onChange: onConfigChange
                          }, null, 8, ["modelValue"])
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
                            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((config.port) = $event)),
                            label: "服务端口",
                            placeholder: "8002",
                            "prepend-inner-icon": "mdi-numeric",
                            hint: "",
                            dense: "",
                            onInput: onConfigChange
                          }, null, 8, ["modelValue"]),
                          _createElementVNode("div", _hoisted_8, [
                            _createVNode(_component_v_icon, {
                              size: "16",
                              color: "info",
                              style: {"margin-right":"4px"}
                            }, {
                              default: _withCtx(() => _cache[17] || (_cache[17] = [
                                _createTextVNode("mdi-information")
                              ])),
                              _: 1,
                              __: [17]
                            }),
                            _cache[18] || (_cache[18] = _createTextVNode(" 容器为 bridge 模式需要手动映射配置的端口 "))
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
            _createElementVNode("div", _hoisted_9, [
              _createElementVNode("div", _hoisted_10, [
                _createVNode(_component_v_icon, {
                  class: "mr-2",
                  color: "info"
                }, {
                  default: _withCtx(() => _cache[19] || (_cache[19] = [
                    _createTextVNode("mdi-folder-multiple-image")
                  ])),
                  _: 1,
                  __: [19]
                }),
                _cache[20] || (_cache[20] = _createTextVNode(" 本地目录配置 "))
              ]),
              _createVNode(_component_v_card_text, null, {
                default: _withCtx(() => [
                  _createVNode(_component_v_row, {
                    dense: "",
                    class: "mb-4"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_v_col, { cols: "12" }, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_11, [
                            _createElementVNode("div", _hoisted_12, [
                              _createVNode(_component_v_icon, {
                                color: "primary",
                                size: "24",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[21] || (_cache[21] = [
                                  _createTextVNode("mdi-monitor")
                                ])),
                                _: 1,
                                __: [21]
                              }),
                              _cache[23] || (_cache[23] = _createElementVNode("span", { class: "directory-title" }, "横屏本地图片目录", -1)),
                              _createVNode(_component_v_chip, {
                                color: "primary",
                                size: "small",
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => _cache[22] || (_cache[22] = [
                                  _createTextVNode("PC/横屏")
                                ])),
                                _: 1,
                                __: [22]
                              })
                            ]),
                            _createVNode(_component_v_text_field, {
                              modelValue: config.pc_path,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((config.pc_path) = $event)),
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
                          _createElementVNode("div", _hoisted_13, [
                            _createElementVNode("div", _hoisted_14, [
                              _createVNode(_component_v_icon, {
                                color: "success",
                                size: "24",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[24] || (_cache[24] = [
                                  _createTextVNode("mdi-cellphone")
                                ])),
                                _: 1,
                                __: [24]
                              }),
                              _cache[26] || (_cache[26] = _createElementVNode("span", { class: "directory-title" }, "竖屏本地图片目录", -1)),
                              _createVNode(_component_v_chip, {
                                color: "success",
                                size: "small",
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => _cache[25] || (_cache[25] = [
                                  _createTextVNode("Mobile/竖屏")
                                ])),
                                _: 1,
                                __: [25]
                              })
                            ]),
                            _createVNode(_component_v_text_field, {
                              modelValue: config.mobile_path,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((config.mobile_path) = $event)),
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
            ]),
            _createElementVNode("div", _hoisted_15, [
              _createElementVNode("div", _hoisted_16, [
                _createVNode(_component_v_icon, {
                  class: "mr-2",
                  color: "primary"
                }, {
                  default: _withCtx(() => _cache[27] || (_cache[27] = [
                    _createTextVNode("mdi-link-variant")
                  ])),
                  _: 1,
                  __: [27]
                }),
                _cache[28] || (_cache[28] = _createTextVNode(" 网络目录配置 "))
              ]),
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
                                default: _withCtx(() => _cache[29] || (_cache[29] = [
                                  _createTextVNode("mdi-monitor")
                                ])),
                                _: 1,
                                __: [29]
                              }),
                              _cache[31] || (_cache[31] = _createElementVNode("span", { class: "directory-title" }, "横屏网络图片地址", -1)),
                              _createVNode(_component_v_chip, {
                                color: "primary",
                                size: "small",
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => _cache[30] || (_cache[30] = [
                                  _createTextVNode("PC/横屏")
                                ])),
                                _: 1,
                                __: [30]
                              })
                            ]),
                            _createVNode(_component_v_text_field, {
                              modelValue: config.network_image_url_pc,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((config.network_image_url_pc) = $event)),
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
                          _createElementVNode("div", _hoisted_19, [
                            _createElementVNode("div", _hoisted_20, [
                              _createVNode(_component_v_icon, {
                                color: "success",
                                size: "24",
                                class: "mr-2"
                              }, {
                                default: _withCtx(() => _cache[32] || (_cache[32] = [
                                  _createTextVNode("mdi-cellphone-link")
                                ])),
                                _: 1,
                                __: [32]
                              }),
                              _cache[34] || (_cache[34] = _createElementVNode("span", { class: "directory-title" }, "竖屏网络图片地址", -1)),
                              _createVNode(_component_v_chip, {
                                color: "success",
                                size: "small",
                                class: "ml-2"
                              }, {
                                default: _withCtx(() => _cache[33] || (_cache[33] = [
                                  _createTextVNode("Mobile/竖屏")
                                ])),
                                _: 1,
                                __: [33]
                              })
                            ]),
                            _createVNode(_component_v_text_field, {
                              modelValue: config.network_image_url_mobile,
                              "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((config.network_image_url_mobile) = $event)),
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
            ]),
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
        }),
        _createVNode(_component_v_card_actions, { class: "px-2 py-1" }, {
          default: _withCtx(() => [
            _createVNode(_component_v_btn, {
              class: "btn-gradient-status",
              onClick: _cache[7] || (_cache[7] = $event => (_ctx.$emit('switch'))),
              "prepend-icon": "mdi-view-dashboard",
              disabled: saving.value,
              size: "small"
            }, {
              default: _withCtx(() => _cache[35] || (_cache[35] = [
                _createTextVNode("状态页")
              ])),
              _: 1,
              __: [35]
            }, 8, ["disabled"]),
            _createVNode(_component_v_spacer),
            _createVNode(_component_v_btn, {
              class: "btn-gradient-reset",
              onClick: resetConfig,
              disabled: saving.value,
              "prepend-icon": "mdi-restore",
              size: "small"
            }, {
              default: _withCtx(() => _cache[36] || (_cache[36] = [
                _createTextVNode("重置")
              ])),
              _: 1,
              __: [36]
            }, 8, ["disabled"]),
            _createVNode(_component_v_btn, {
              class: "btn-gradient-save",
              disabled: !isConfigValid() || saving.value,
              onClick: saveConfig,
              loading: saving.value,
              "prepend-icon": "mdi-content-save",
              size: "small"
            }, {
              default: _withCtx(() => _cache[37] || (_cache[37] = [
                _createTextVNode("保存配置")
              ])),
              _: 1,
              __: [37]
            }, 8, ["disabled", "loading"]),
            _createVNode(_component_v_btn, {
              class: "btn-gradient-close",
              onClick: _cache[8] || (_cache[8] = $event => (_ctx.$emit('close'))),
              "prepend-icon": "mdi-close",
              disabled: saving.value,
              size: "small"
            }, {
              default: _withCtx(() => _cache[38] || (_cache[38] = [
                _createTextVNode("关闭")
              ])),
              _: 1,
              __: [38]
            }, 8, ["disabled"])
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
const ConfigComponent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-cdf50601"]]);

export { ConfigComponent as default };
