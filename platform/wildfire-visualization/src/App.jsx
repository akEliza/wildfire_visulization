import React, { useState } from 'react';
import { AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemText, Box, Divider } from '@mui/material';

const drawerWidth = 240;
const variables = ["theta", "rhof", "velocity", "vorticity"];
const terrains = [
  "headcurve40",
  "headcurve80",
  "headcurve320",
  "backcurve40",
  "backcurve80",
  "backcurve320",
  "valley_losAlamos"
];

export default function App() {
  const [selectedVar, setSelectedVar] = useState("rhof");
  const [selectedTerrain, setSelectedTerrain] = useState("headcurve40");

  const fileExt = selectedVar === "rhof" ? "png" : "mp4";
  const filePath = `results/${selectedVar}/${selectedTerrain}.${fileExt}`;

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Wildfire Visualization
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <Typography variant="h6" sx={{ pl: 2, pt: 1 }}>Variables</Typography>
            {variables.map((v) => (
              <ListItem
                button
                key={v}
                selected={selectedVar === v}
                onClick={() => setSelectedVar(v)}
              >
                <ListItemText primary={v} />
              </ListItem>
            ))}
          </List>
          <Divider />
          <List>
            <Typography variant="h6" sx={{ pl: 2, pt: 1 }}>Terrains</Typography>
            {terrains.map((t) => (
              <ListItem
                button
                key={t}
                selected={selectedTerrain === t}
                onClick={() => setSelectedTerrain(t)}
              >
                <ListItemText primary={t} />
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Box sx={{ border: '1px solid #ccc', borderRadius: 1, p: 2 }}>
          {selectedVar === "rhof" ? (
            <img src={filePath} alt="Visualization" style={{ width: '100%', height: 'auto' }} />
          ) : (
            <video key={filePath} controls style={{ width: '100%', height: 'auto' }}>
              <source src={filePath} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          )}
        </Box>
      </Box>
    </Box>
  );
}
