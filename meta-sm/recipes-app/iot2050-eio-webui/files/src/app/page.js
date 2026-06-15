/* eslint-disable react/prop-types */
'use client';

import * as React from 'react';
import Alert from '@mui/material/Alert';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Divider from '@mui/material/Divider';
import Stack from '@mui/material/Stack';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import PropTypes from 'prop-types';
import ChecklistIcon from '@mui/icons-material/Checklist';
import { range } from 'lodash';
import YAML from 'yaml';
import SlotInfo from '@/components/SlotInfo';
import { exportYamlConfig, importYamlConfig } from '@/lib/smConfig/smConfig';

const EIO_WEBUI_BRIDGE_PORT = 5021;

function getCockpit () {
  return globalThis.cockpit;
}

function TabPanel (props) {
  const { value, index, configData, updateSlot, ...other } = props;

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
          <SlotInfo slotNum={value} configData={configData} updateSlot={updateSlot} />
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
  configData: PropTypes.object.isRequired,
  index: PropTypes.number.isRequired,
  updateSlot: PropTypes.func.isRequired,
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

function getEioBridgeClient () {
  const cockpit = getCockpit();

  if (!cockpit) {
    throw new Error('Cockpit runtime is unavailable');
  }

  return cockpit.http(EIO_WEBUI_BRIDGE_PORT);
}

async function requestBridge (method, path, body) {
  const http = getEioBridgeClient();

  try {
    const responseText = method === 'GET'
      ? await http.get(path, undefined, { Accept: 'application/json' })
      : await http.request({
          method,
          path,
          body: JSON.stringify(body),
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json'
          }
        });

    return JSON.parse(responseText);
  } catch (error) {
    throw new Error(error?.message || error?.reason || String(error));
  }
}

async function deployConfig (payload) {
  const response = await requestBridge('PUT', '/api/v1/eio/config', {
    yaml_data: payload
  });

  if (!response.ok) {
    throw new Error(response.message || 'Configuration deployment failed.');
  }
}

async function retrieveConfigFromDevice () {
  const response = await requestBridge('GET', '/api/v1/eio/config');

  if (!response.ok) {
    throw new Error(response.message || 'Configuration retrieval failed.');
  }

  return response.data?.yaml_data;
}

export default function HomePage () {
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
  const inputFile = React.useRef(null);

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

  const setResultBanner = (severity, message) => {
    setResultFromIoT({
      display: 'block',
      severity,
      message
    });
  };

  const resetResultBanner = () => {
    setResultFromIoT({
      display: 'none',
      severity: 'success',
      message: ''
    });
  };

  const exportConfigFile = () => {
    const fileData = getYamlStr(configs);
    const blob = new Blob([fileData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.download = 'config.yaml';
    link.href = url;
    link.click();
    URL.revokeObjectURL(url);
  };

  const importConfFile = () => {
    inputFile.current.click();
  };

  const deployConfToIOT = async () => {
    resetResultBanner();

    try {
      const payload = getYamlStr(configs);
      await deployConfig(payload);

      setResultBanner('success', 'Configuration deployed successfully.');
    } catch (error) {
      setResultBanner('error', error.message || String(error));
    }
  };

  const retrieveConfFromIOT = async () => {
    resetResultBanner();

    try {
      const yamlOutput = await retrieveConfigFromDevice();

      const parsed = YAML.parse(yamlOutput);
      if (parsed && typeof parsed === 'object') {
        setConfigs(importYamlConfig(parsed));
        setResultBanner('success', 'Configuration retrieved successfully.');
      } else {
        setResultBanner('error', 'Empty configuration returned.');
      }
    } catch (error) {
      setResultBanner('error', error.message || String(error));
    }
  };

  const handleFileChange = (event) => {
    const fileObj = event.target.files && event.target.files[0];
    if (!fileObj) {
      return;
    }

    event.target.value = null;

    const reader = new FileReader();
    reader.onload = function () {
      try {
        setConfigs(importYamlConfig(YAML.parse(reader.result)));
        resetResultBanner();
      } catch (error) {
        setResultBanner('error', error.message || String(error));
      }
    };
    reader.readAsText(fileObj);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#fafafa' }}>
      <AppBar position="static" sx={{ mb: 4, bgcolor: '#007993' }}>
        <Toolbar sx={{ backgroundColor: '#fff' }}>
          <Box sx={{ mr: 2, display: 'flex', alignItems: 'center' }}>
            <Box
              component="img"
              src="./icon-siemens.svg"
              alt="SIEMENS"
              sx={{ height: 22 }}
            />
          </Box>
          <ChecklistIcon sx={{ color: 'black', mr: 1 }} />
          <Typography variant="h5" noWrap component="div" color="black">
            SIMATIC IOT2050 EIO Config
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'stretch'
          }}
        >
          <Stack spacing={2}>
            <input type='file' id='file' onChange={handleFileChange} ref={inputFile} style={{ display: 'none' }} />

            <Stack spacing={2} direction="row" justifyContent="flex-end" flexWrap="wrap" useFlexGap>
              <Button variant="contained" onClick={importConfFile} sx={{ backgroundColor: '#007993' }}>
                <Box sx={{ textTransform: 'none' }}>Import Configuration</Box>
              </Button>
              <Button variant="contained" onClick={exportConfigFile} sx={{ backgroundColor: '#007993' }}>
                <Box sx={{ textTransform: 'none' }}>Export Configuration</Box>
              </Button>
              <Button variant="contained" onClick={deployConfToIOT} sx={{ backgroundColor: '#007993' }}>
                <Box sx={{ textTransform: 'none' }}>Deploy to IOT</Box>
              </Button>
              <Button variant="contained" onClick={retrieveConfFromIOT} sx={{ backgroundColor: '#007993' }}>
                <Box sx={{ textTransform: 'none' }}>Retrieve from IOT</Box>
              </Button>
            </Stack>

            <Stack sx={{ width: '100%', display: resultFromIoT.display }} spacing={2}>
              <Alert
                onClose={resetResultBanner}
                severity={resultFromIoT.severity}
              >{resultFromIoT.message}</Alert>
            </Stack>

            <Divider />

            <Box sx={{ width: '100%' }}>
              <AppBar position="static" sx={{ bgcolor: '#007993' }}>
                <Tabs
                  value={curSlot}
                  onChange={handleChange}
                  textColor="inherit"
                  aria-label="secondary tabs"
                  variant="scrollable"
                  scrollButtons="auto"
                  TabIndicatorProps={{ style: { backgroundColor: '#fff' } }}
                >
                  {range(1, 7).map((index) => (
                    <Tab
                      sx={{ textTransform: 'none' }}
                      key={index}
                      label={'Slot ' + index}
                      {...a11yProps(index)}
                      disabled={slotDisabledProps(index)}
                    />
                  ))}
                </Tabs>
              </AppBar>
              {range(0, 6).map((index) => (
                <TabPanel
                  key={index}
                  value={curSlot}
                  index={index}
                  configData={configs.config[index]}
                  updateSlot={updateSlot}
                />
              ))}
            </Box>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
}
