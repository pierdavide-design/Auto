global.crypto = require('crypto');

const express = require('express');
const { Client, RemoteAuth } = require('whatsapp-web.js');
const { MongoStore } = require('wwebjs-mongo');
const mongoose = require('mongoose');
const qrcodeTerminal = require('qrcode-terminal');
const QRCode = require('qrcode');

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

let isReady = false;
let currentQrImage = null; // Memorizza l'immagine QR generata

// Endpoint per vedere il QR code formattato da browser
app.get('/qr', async (req, res) => {
    if (isReady) {
        return res.send('<h2>WhatsApp è già connesso e pronto!</h2>');
    }
    if (!currentQrImage) {
        return res.send('<h2>In attesa della generazione del codice QR... Ricarica tra qualche secondo.</h2>');
    }
    res.send(`
        <html>
            <body style="display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; font-family:sans-serif; background:#f0f2f5;">
                <h2>Scansiona il codice QR con WhatsApp</h2>
                <img src="${currentQrImage}" style="border: 10px solid white; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);" />
                <p>Apri WhatsApp > Dispositivi collegati > Inquadra il codice</p>
            </body>
        </html>
    `);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`[SERVER] Gateway Node.js attivo sulla porta ${PORT}`);
});

const MONGO_URI = process.env.MONGO_URI;

if (!MONGO_URI) {
    console.error("[ERRORE CRITICO] MONGO_URI mancante nelle variabili d'ambiente!");
    process.exit(1);
}

mongoose.connect(MONGO_URI).then(() => {
    console.log('[MONGO] Connessione a MongoDB Atlas riuscita.');
    
    const store = new MongoStore({ mongoose: mongoose });

    const client = new Client({
        authStrategy: new RemoteAuth({
            store: store,
            backupSyncIntervalMs: 300000
        }),
        webVersionCache: {
            type: 'remote',
            remotePath: 'https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/2.2412.54.html',
        },
        puppeteer: {
            executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || null,
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--single-process'
            ]
        }
    });

    client.on('qr', async (qr) => {
        console.log('[WHATSAPP] Nuovo codice QR generato.');
        qrcodeTerminal.generate(qr, { small: true });
        
        // Converte il QR in un'immagine Base64 per la pagina web
        try {
            currentQrImage = await QRCode.toDataURL(qr);
        } catch (err) {
            console.error('[ERRORE QR GENERATION]:', err);
        }
    });

    client.on('ready', () => {
        isReady = true;
        currentQrImage = null;
        console.log('[WHATSAPP] Client connesso e pronto!');
    });

    client.on('remote_session_saved', () => {
        console.log('[WHATSAPP] Sessione salvata con successo su MongoDB!');
    });

    client.on('disconnected', (reason) => {
        isReady = false;
        currentQrImage = null;
        console.log('[WHATSAPP] Client disconnesso:', reason);
    });

    const handleSendMessage = async (req, res) => {
        if (!isReady) {
            return res.status(503).json({ error: 'WhatsApp non è ancora pronto.' });
        }

        const body = req.body || {};
        const message = body.message || body.testo || body.text;
        const group_name = body.group_name || body.gruppo || body.group;

        if (!message || !group_name) {
            return res.status(400).json({ error: 'Parametri insufficienti.' });
        }

        try {
            const chats = await client.getChats();
            const group = chats.find(c => 
                c.isGroup && c.name.toLowerCase().includes(group_name.toLowerCase())
            );

            if (!group) {
                return res.status(404).json({ error: `Gruppo "${group_name}" non trovato.` });
            }

            await group.sendMessage(message);
            console.log(`[WHATSAPP] Messaggio inviato a: ${group.name}`);
            return res.json({ status: 'ok', group: group.name });

        } catch (err) {
            console.error('[WHATSAPP ERRORE INVIO]:', err);
            return res.status(500).json({ error: err.message || String(err) });
        }
    };

    app.post('/send', handleSendMessage);
    app.post('/send-message', handleSendMessage);

    client.initialize();
}).catch(err => {
    console.error('[MONGO ERRORE]:', err);
});