import { importShared } from './__federation_fn_import-a2e11483.js';
import { w as consoleWarn, J as IN_BROWSER, b as getCurrentInstance, aM as mergeDeep, aN as createDefaults, aO as createDisplay, aP as createTheme, aQ as createIcons, aR as createLocale, aS as createDate, aT as createGoTo, Z as defineComponent, aU as DefaultsSymbol, aV as DisplaySymbol, aW as ThemeSymbol, aX as IconSymbol, aY as LocaleSymbol, aZ as DateOptionsSymbol, a_ as DateAdapterSymbol, a$ as GoToSymbol } from './date-b36049d0.js';
export { ay as useDate, b0 as useDefaults, V as useDisplay, W as useGoTo, aC as useLayout, M as useLocale, u as useRtl, E as useTheme } from './date-b36049d0.js';

/**
 * Centralized key alias mapping for consistent key normalization across the hotkey system.
 *
 * This maps various user-friendly aliases to canonical key names that match
 * KeyboardEvent.key values (in lowercase) where possible.
 */
const keyAliasMap = {
  // Modifier aliases (from vue-use, other libraries, and current implementation)
  control: 'ctrl',
  command: 'cmd',
  option: 'alt',
  // Arrow key aliases (common abbreviations)
  up: 'arrowup',
  down: 'arrowdown',
  left: 'arrowleft',
  right: 'arrowright',
  // Other common key aliases
  esc: 'escape',
  spacebar: ' ',
  space: ' ',
  return: 'enter',
  del: 'delete',
  // Symbol aliases (existing from hotkey-parsing.ts)
  minus: '-',
  hyphen: '-'
};

/**
 * Normalizes a key string to its canonical form using the alias map.
 *
 * @param key - The key string to normalize
 * @returns The canonical key name in lowercase
 */
function normalizeKey(key) {
  const lowerKey = key.toLowerCase();
  return keyAliasMap[lowerKey] || lowerKey;
}

// Utilities

/**
 * Splits a single combination string into individual key parts.
 *
 * A combination is a set of keys that must be pressed simultaneously.
 * e.g. `ctrl+k`, `shift--`
 */
function splitKeyCombination(combination) {
  let isInternal = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
  if (!combination) {
    if (!isInternal) consoleWarn('Invalid hotkey combination: empty string provided');
    return [];
  }

  // --- VALIDATION ---
  const startsWithPlusOrUnderscore = combination.startsWith('+') || combination.startsWith('_');
  const hasInvalidLeadingSeparator =
  // Starts with a single '+' or '_' followed by a non-separator character (e.g. '+a', '_a')
  startsWithPlusOrUnderscore && !(combination.startsWith('++') || combination.startsWith('__'));
  const hasInvalidStructure =
  // Invalid leading separator patterns
  combination.length > 1 && hasInvalidLeadingSeparator ||
  // Disallow literal + or _ keys (they require shift)
  combination.includes('++') || combination.includes('__') || combination === '+' || combination === '_' ||
  // Ends with a separator that is not part of a doubled literal
  combination.length > 1 && (combination.endsWith('+') || combination.endsWith('_')) && combination.at(-2) !== combination.at(-1) ||
  // Stand-alone doubled separators (dangling)
  combination === '++' || combination === '--' || combination === '__';
  if (hasInvalidStructure) {
    if (!isInternal) consoleWarn(`Invalid hotkey combination: "${combination}" has invalid structure`);
    return [];
  }
  const keys = [];
  let buffer = '';
  const flushBuffer = () => {
    if (buffer) {
      keys.push(normalizeKey(buffer));
      buffer = '';
    }
  };
  for (let i = 0; i < combination.length; i++) {
    const char = combination[i];
    const nextChar = combination[i + 1];
    if (char === '+' || char === '_' || char === '-') {
      if (char === nextChar) {
        flushBuffer();
        keys.push(char);
        i++;
      } else if (char === '+' || char === '_') {
        flushBuffer();
      } else {
        buffer += char;
      }
    } else {
      buffer += char;
    }
  }
  flushBuffer();

  // Within a combination, `-` is only valid as a literal key (e.g., `ctrl+-`).
  // `-` cannot be part of a longer key name within a combination.
  const hasInvalidMinus = keys.some(key => key.length > 1 && key.includes('-') && key !== '--');
  if (hasInvalidMinus) {
    if (!isInternal) consoleWarn(`Invalid hotkey combination: "${combination}" has invalid structure`);
    return [];
  }
  if (keys.length === 0 && combination) {
    return [normalizeKey(combination)];
  }
  return keys;
}

/**
 * Splits a hotkey string into its constituent combination groups.
 *
 * A sequence is a series of combinations that must be pressed in order.
 * e.g. `a-b`, `ctrl+k-p`
 */
function splitKeySequence(str) {
  if (!str) {
    consoleWarn('Invalid hotkey sequence: empty string provided');
    return [];
  }

  // A sequence is invalid if it starts or ends with a separator,
  // unless it is part of a combination (e.g., `shift+-`).
  const hasInvalidStart = str.startsWith('-') && !['---', '--+'].includes(str);
  const hasInvalidEnd = str.endsWith('-') && !str.endsWith('+-') && !str.endsWith('_-') && str !== '-' && str !== '---';
  if (hasInvalidStart || hasInvalidEnd) {
    consoleWarn(`Invalid hotkey sequence: "${str}" contains invalid combinations`);
    return [];
  }
  const result = [];
  let buffer = '';
  let i = 0;
  while (i < str.length) {
    const char = str[i];
    if (char === '-') {
      // Determine if this hyphen is part of the current combination
      const prevChar = str[i - 1];
      const prevPrevChar = i > 1 ? str[i - 2] : undefined;
      const precededBySinglePlusOrUnderscore = (prevChar === '+' || prevChar === '_') && prevPrevChar !== '+';
      if (precededBySinglePlusOrUnderscore) {
        // Treat as part of the combination (e.g., 'ctrl+-')
        buffer += char;
        i++;
      } else {
        // Treat as sequence separator
        if (buffer) {
          result.push(buffer);
          buffer = '';
        } else {
          // Empty buffer means we have a literal '-' key
          result.push('-');
        }
        i++;
      }
    } else {
      buffer += char;
      i++;
    }
  }

  // Add final buffer if it exists
  if (buffer) {
    result.push(buffer);
  }

  // Collapse runs of '-' so that every second '-' is removed
  const collapsed = [];
  let minusCount = 0;
  for (const part of result) {
    if (part === '-') {
      if (minusCount % 2 === 0) collapsed.push('-');
      minusCount++;
    } else {
      minusCount = 0;
      collapsed.push(part);
    }
  }

  // Validate that each part of the sequence is a valid combination
  const areAllValid = collapsed.every(s => splitKeyCombination(s, true).length > 0);
  if (!areAllValid) {
    consoleWarn(`Invalid hotkey sequence: "${str}" contains invalid combinations`);
    return [];
  }
  return collapsed;
}

const {onBeforeUnmount,toValue,watch} = await importShared('vue');
function useHotkey(keys, callback) {
  let options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : {};
  if (!IN_BROWSER) return function () {};
  const {
    event = 'keydown',
    inputs = false,
    preventDefault = true,
    sequenceTimeout = 1000
  } = options;
  const isMac = navigator?.userAgent?.includes('Macintosh') ?? false;
  let timeout = 0;
  let keyGroups;
  let isSequence = false;
  let groupIndex = 0;
  function clearTimer() {
    if (!timeout) return;
    clearTimeout(timeout);
    timeout = 0;
  }
  function isInputFocused() {
    if (toValue(inputs)) return false;
    const activeElement = document.activeElement;
    return activeElement && (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA' || activeElement.isContentEditable || activeElement.contentEditable === 'true');
  }
  function resetSequence() {
    groupIndex = 0;
    clearTimer();
  }
  function handler(e) {
    const group = keyGroups[groupIndex];
    if (!group || isInputFocused()) return;
    if (!matchesKeyGroup(e, group)) {
      if (isSequence) resetSequence();
      return;
    }
    if (toValue(preventDefault)) e.preventDefault();
    if (!isSequence) {
      callback(e);
      return;
    }
    clearTimer();
    groupIndex++;
    if (groupIndex === keyGroups.length) {
      callback(e);
      resetSequence();
      return;
    }
    timeout = window.setTimeout(resetSequence, toValue(sequenceTimeout));
  }
  function cleanup() {
    window.removeEventListener(toValue(event), handler);
    clearTimer();
  }
  watch(() => toValue(keys), function (unrefKeys) {
    cleanup();
    if (unrefKeys) {
      const groups = splitKeySequence(unrefKeys.toLowerCase());
      isSequence = groups.length > 1;
      keyGroups = groups;
      resetSequence();
      window.addEventListener(toValue(event), handler);
    }
  }, {
    immediate: true
  });

  // Watch for changes in the event type to re-register the listener
  watch(() => toValue(event), function (newEvent, oldEvent) {
    if (oldEvent && keyGroups && keyGroups.length > 0) {
      window.removeEventListener(oldEvent, handler);
      window.addEventListener(newEvent, handler);
    }
  });
  try {
    getCurrentInstance('useHotkey');
    onBeforeUnmount(cleanup);
  } catch {
    // Not in Vue setup context
  }
  function parseKeyGroup(group) {
    const MODIFIERS = ['ctrl', 'shift', 'alt', 'meta', 'cmd'];

    // Use the shared combination splitting logic
    const parts = splitKeyCombination(group.toLowerCase());

    // If the combination is invalid, return empty result
    if (parts.length === 0) {
      return {
        modifiers: Object.fromEntries(MODIFIERS.map(m => [m, false])),
        actualKey: undefined
      };
    }
    const modifiers = Object.fromEntries(MODIFIERS.map(m => [m, false]));
    let actualKey;
    for (const part of parts) {
      if (MODIFIERS.includes(part)) {
        modifiers[part] = true;
      } else {
        actualKey = part;
      }
    }
    return {
      modifiers,
      actualKey
    };
  }
  function matchesKeyGroup(e, group) {
    const {
      modifiers,
      actualKey
    } = parseKeyGroup(group);
    const expectCtrl = modifiers.ctrl || !isMac && (modifiers.cmd || modifiers.meta);
    const expectMeta = isMac && (modifiers.cmd || modifiers.meta);
    return e.ctrlKey === expectCtrl && e.metaKey === expectMeta && e.shiftKey === modifiers.shift && e.altKey === modifiers.alt && e.key.toLowerCase() === actualKey?.toLowerCase();
  }
  return cleanup;
}

const {effectScope,nextTick,reactive} = await importShared('vue');
function createVuetify() {
  let vuetify = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  const {
    blueprint,
    ...rest
  } = vuetify;
  const options = mergeDeep(blueprint, rest);
  const {
    aliases = {},
    components = {},
    directives = {}
  } = options;
  const scope = effectScope();
  return scope.run(() => {
    const defaults = createDefaults(options.defaults);
    const display = createDisplay(options.display, options.ssr);
    const theme = createTheme(options.theme);
    const icons = createIcons(options.icons);
    const locale = createLocale(options.locale);
    const date = createDate(options.date, locale);
    const goTo = createGoTo(options.goTo, locale);
    function install(app) {
      for (const key in directives) {
        app.directive(key, directives[key]);
      }
      for (const key in components) {
        app.component(key, components[key]);
      }
      for (const key in aliases) {
        app.component(key, defineComponent({
          ...aliases[key],
          name: key,
          aliasName: aliases[key].name
        }));
      }
      const appScope = effectScope();
      appScope.run(() => {
        theme.install(app);
      });
      app.onUnmount(() => appScope.stop());
      app.provide(DefaultsSymbol, defaults);
      app.provide(DisplaySymbol, display);
      app.provide(ThemeSymbol, theme);
      app.provide(IconSymbol, icons);
      app.provide(LocaleSymbol, locale);
      app.provide(DateOptionsSymbol, date.options);
      app.provide(DateAdapterSymbol, date.instance);
      app.provide(GoToSymbol, goTo);
      if (IN_BROWSER && options.ssr) {
        if (app.$nuxt) {
          app.$nuxt.hook('app:suspense:resolve', () => {
            display.update();
          });
        } else {
          const {
            mount
          } = app;
          app.mount = function () {
            const vm = mount(...arguments);
            nextTick(() => display.update());
            app.mount = mount;
            return vm;
          };
        }
      }
      {
        app.mixin({
          computed: {
            $vuetify() {
              return reactive({
                defaults: inject.call(this, DefaultsSymbol),
                display: inject.call(this, DisplaySymbol),
                theme: inject.call(this, ThemeSymbol),
                icons: inject.call(this, IconSymbol),
                locale: inject.call(this, LocaleSymbol),
                date: inject.call(this, DateAdapterSymbol)
              });
            }
          }
        });
      }
    }
    function unmount() {
      scope.stop();
    }
    return {
      install,
      unmount,
      defaults,
      display,
      theme,
      icons,
      locale,
      date,
      goTo
    };
  });
}
const version = "3.9.0";
createVuetify.version = version;

// Vue's inject() can only be used in setup
function inject(key) {
  const vm = this.$;
  const provides = vm.parent?.provides ?? vm.vnode.appContext?.provides;
  if (provides && key in provides) {
    return provides[key];
  }
}

export { createVuetify, useHotkey, version };
