DecentraDNS - Decentralized Domain Name System

Technologies Used:
- React
- Flask
- MultiChain (Blockchain)
- Python

Description:
A decentralized domain name system built using MultiChain blockchain, Flask backend, and a React frontend. Secure, transparent, and censorship-resistant domain registration and management.

Features:
- Decentralized Domain Registration
- Domain Info Lookup
- Secure Ownership Transfer
- Domain History Tracking
- Real-time Dashboard
- RESTful API
- Modern Responsive Web UI

Tech Stack:
- Frontend: React, React Router, Axios
- Backend: Flask (Python), MultiChain JSON-RPC
- Blockchain: MultiChain (Private), Stream-based data storage
- Communication: JSON-RPC

Project Structure:
decentra-dns/
├── Backend/
│   ├── app.py              (Flask server with API routes)
│   ├── mcdns.py            (MultiChain Domain logic)
│   ├── multichain.py       (MultiChain RPC wrapper)
│   └── requirements.txt    (Python dependencies)
├── Frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── styles.css
│   │   └── components/     (UI components)
│   └── package.json
└── README.txt

Installation & Setup:

Prerequisites:
- Python 3.7 or above
- Node.js 14 or above
- MultiChain installed (https://www.multichain.com/download/)
- Git

MultiChain Setup:
multichain-util create dns
multichaind dns -daemon

Clone the Repository:
git clone https://github.com/yourusername/decentra-dns.git
cd decentra-dns

Backend Setup:
cd Backend
pip install -r requirements.txt

Update MultiChain Config in app.py:
rpchost = '127.0.0.1'
rpcport = 4384
rpcuser = 'multichainrpc'
rpcpassword = 'your-rpc-password'

Frontend Setup:
cd Frontend
npm install
npm install react-router-dom

Running the Application:

Start MultiChain Node:
multichaind dns -daemon

Run Flask Backend:
cd Backend
python app.py
(Available at http://localhost:5000)

Run React Frontend:
cd Frontend
npm start
(Available at http://localhost:3000)

API Endpoints:

GET    /api/domains                 - Fetch all registered domains
POST   /api/domains/register        - Register a new domain
GET    /api/domains/{domain}        - Fetch domain details
POST   /api/domains/{domain}/transfer - Transfer domain to another user
GET    /api/domains/{domain}/history - View domain transaction history

Example API Call:
Register a domain:
curl -X POST http://localhost:5000/api/domains/register \
-H "Content-Type: application/json" \
-d '{"domain": "example.dns", "owner": "user1", "ip": "192.168.1.1"}'

Configuration:

Environment Variables (Optional):
MULTICHAIN_HOST=127.0.0.1
MULTICHAIN_PORT=4384
MULTICHAIN_USER=multichainrpc
MULTICHAIN_PASSWORD=your-password
MULTICHAIN_CHAIN=dns
FLASK_PORT=5000
REACT_PORT=3000

Security Best Practices:
- Private Key Management: Keep MultiChain wallet keys secure
- Restrict RPC Access: Allow only authorized connections
- Input Validation: Validate all domain input fields
- CORS: Configure for production deployments
