/* eslint-disable react/prop-types */
'use client';

import { exportYamlConfig, importYamlConfig } from '@/lib/smConfig/smConfig';
// import { useTheme } from '@mui/material/styles';
import Container from '@mui/material/Container';
import SlotInfo from '@/components/SlotInfo';
import Divider from '@mui/material/Divider';
import AppBar from '@mui/material/AppBar';
import Button from '@mui/material/Button';
import Alert from '@mui/material/Alert';
import Stack from '@mui/material/Stack';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import PropTypes from 'prop-types';
import { range } from 'lodash';
import * as React from 'react';
import { useRef } from 'react';
import YAML from 'yaml';

function TabPanel (props) {
  const { children, value, index, configData, updateSlot, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <SlotInfo slotNum={value} configData={configData} updateSlot={updateSlot} ></SlotInfo>
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired
};

function a11yProps (index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`
  };
}

function getYamlStr (config) {
  const doc = new YAML.Document(exportYamlConfig(config));
  return doc.toString();
}

export default function SMConfPage () {
  // const theme = useTheme();
  const [curSlot, setCurSlot] = React.useState(0);
  const [configs, setConfigs] = React.useState({
    version: 1,
    config: [
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' },
      { mlfb: 'None' }
    ]
  });

  const [resultFromIoT, setResultFromIoT] = React.useState({
    display: 'none',
    severity: 'success',
    message: ''
  });

  const inputFile = useRef(null);

  const slotDisabledProps = (index) => {
    const arrayIndex = index - 1;
    if (arrayIndex !== 0 && configs.config[arrayIndex - 1].mlfb === 'None') {
      return true;
    }
    return false;
  };

  const updateSlot = (index, conf) => {
    const newConfigs = {
      ...configs
    };
    newConfigs.config[index] = { ...conf };
    if (conf.mlfb === 'None') {
      for (let i = index + 1; i < configs.config.length; i++) {
        newConfigs.config[i] = conf;
      }
    }
    setConfigs(newConfigs);
  };

  const handleChange = (event, newSlot) => {
    setCurSlot(newSlot);
  };

  const exportConfigFile = (event) => {
    const fileData = getYamlStr(configs);
    const blob = new Blob([fileData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = 'config.yaml';
    link.href = url;
    link.click();
  };

  const importConfFile = (event) => {
    inputFile.current.click();
  };

  const deployConfToIOT = async (event) => {
    setResultFromIoT({
      display: 'none',
      severity: 'success',
      message: ''
    });
    const yamlConfig = exportYamlConfig(configs);

    const response = await fetch('/deploy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(yamlConfig)
    });
    response.json().then((data) => {
      let newSeverity = 'success';
      if (data.message.status !== 0) {
        newSeverity = 'error';
      }
      setResultFromIoT({
        display: 'block',
        severity: newSeverity,
        message: data.message.message
      });
    }, (err) => {
      setResultFromIoT({
        display: 'block',
        severity: 'error',
        message: JSON.stringify(err)
      });
    });
  };

  const retrieveConfFromIOT = async (event) => {
    setResultFromIoT({
      display: 'none',
      severity: 'success',
      message: ''
    });
    const response = await fetch('/retrieve', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    response.json().then((data) => {
      let newSeverity = 'success';
      if (data.message.status !== 0) {
        newSeverity = 'error';
      }
      setResultFromIoT({
        display: 'block',
        severity: newSeverity,
        message: data.message.message
      });
      setConfigs(importYamlConfig(YAML.parse(data.message.yaml_data)));
    }, (err) => {
      setResultFromIoT({
        display: 'block',
        severity: 'error',
        message: JSON.stringify(err)
      });
    });
  };

  const handleFileChange = (event) => {
    const fileObj = event.target.files && event.target.files[0];
    if (!fileObj) {
      return;
    }

    // reset file input
    event.target.value = null;

    const reader = new FileReader();
    reader.onload = function (e) {
      const content = reader.result;
      setConfigs(importYamlConfig(YAML.parse(content)));
    };
    reader.readAsText(fileObj);
  };

  const debugPrint = (event) => {
    console.log(configs);
  };

  return (
    <Container>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'stretch'
        }}
      >
        <Stack spacing={2}>
          <input type='file' id='file' onChange={handleFileChange} ref={inputFile} style={{ display: 'none' }}/>

          <Stack spacing={2} direction="row" justifyContent="flex-end">
            <Button variant="contained" onClick={importConfFile}>
              <Box sx={{ textTransform: 'none' }}>Import Configuration</Box>
            </Button>
            <Button variant="contained" onClick={exportConfigFile}>
              <Box sx={{ textTransform: 'none' }}>Export Configuration</Box>
            </Button>
            <Button variant="contained" onClick={deployConfToIOT}>
              <Box sx={{ textTransform: 'none' }}>Deploy to IOT</Box>
            </Button>
            <Button variant="contained" onClick={retrieveConfFromIOT}>
              <Box sx={{ textTransform: 'none' }}>Retrieve from IOT</Box>
            </Button>
            <Button variant="contained" onClick={debugPrint} sx={{ display: 'none' }}>
              <Box sx={{ textTransform: 'none' }}>Debug Print</Box>
            </Button>
          </Stack>
          <Stack sx={{ width: '100%', display: resultFromIoT.display }} spacing={2}>
            <Alert
              onClose={() => {
                setResultFromIoT({
                  display: 'none',
                  severity: resultFromIoT.severity,
                  message: resultFromIoT.message
                });
              }}
              severity={resultFromIoT.severity}
            >{resultFromIoT.message}</Alert>
          </Stack>
          <Divider />

          <Box sx={{ width: '100%' }}>
            {/* <Box sx={{ borderBottom: 1, borderColor: 'divider' }}> */}
            <AppBar position="static">
              <Tabs
                value={curSlot}
                onChange={handleChange}
                textColor="inherit"
                indicatorColor="secondary"
                aria-label="secondary tabs"
              >
                { range(1, 7).map((index) => (
                    <Tab
                      sx={{ textTransform: 'none' }}
                      key={index}
                      label={'Slot ' + index}
                      {...a11yProps(index)}
                      disabled={slotDisabledProps(index)}
                    />
                ))
                }
              </Tabs>
            </AppBar>
            {/* </Box> */}
            { range(0, 6).map((index) => (
              <TabPanel
                key={index}
                value={curSlot}
                index={index}
                configData={configs.config[index]}
                updateSlot={updateSlot} >
              </TabPanel>
            ))
            }
          </Box>
        </Stack>
      </Box>
    </Container>
  );
}
