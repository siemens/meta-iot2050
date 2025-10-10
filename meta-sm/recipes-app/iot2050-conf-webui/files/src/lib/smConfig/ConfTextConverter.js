export default class ConfTextConverter {
  constructor (table) {
    this.table = table;
  }

  uiToYaml (key, text, scenario = 'all') {
    for (const item of this.table) {
      for (const keyRe of item.keys) {
        if (!keyRe.test(key)) { continue; };
        for (const rule of item.rules) {
          if (rule.scenario === scenario) {
            for (const m of rule.mapping) {
              if (text === m.ui) {
                return m.yaml;
              }
            }
          }
        }
      }
    }

    return 'ERROR!';
  }

  yamlToUi (key, text, scenario = 'all') {
    for (const item of this.table) {
      for (const keyRe of item.keys) {
        if (!keyRe.test(key)) { continue; };
        for (const rule of item.rules) {
          if (rule.scenario === scenario) {
            for (const m of rule.mapping) {
              if (text === m.yaml) {
                return m.ui;
              }
            }
          }
        }
      }
    }

    return 'ERROR!';
  }
}
