// server.js
const express = require('express');
const app = express();
const port = 3000;

let storedIP = null; // Variable to store the IP address

app.use(express.static('public')); // Serve files from the "public" folder

// Endpoint to log IP address
app.get('/log-ip', (req, res) => {
    storedIP = req.ip; // Save the IP address
    console.log(`IP logged: ${storedIP}`);
    res.send('Panda location has been logged!');
});

// Endpoint to retrieve stored IP address
app.get('/get-ip', (req, res) => {
    if (storedIP) {
        res.json({ ip: storedIP });
    } else {
        res.status(404).send('No IP address stored yet.');
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
