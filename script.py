from pathlib import Path
base = Path('output/nodejs_backend')
base.mkdir(parents=True, exist_ok=True)
files = {
'package.json': '''{
  "name": "contextmind-backend",
  "version": "1.0.0",
  "main": "src/server.js",
  "type": "module",
  "scripts": {
    "dev": "node src/server.js",
    "start": "node src/server.js"
  },
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.4.5",
    "express": "^4.21.2",
    "mongoose": "^8.9.5"
  }
}''',
'.env.example': '''PORT=5000
MONGO_URI=mongodb://127.0.0.1:27017/contextmind
JWT_SECRET=change_this
''',
'src/server.js': '''import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import remindersRouter from './routes/reminders.js';
import dashboardRouter from './routes/dashboard.js';
import authRouter from './routes/auth.js';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

app.get('/', (req, res) => res.json({ ok: true, message: 'ContextMind API running' }));
app.use('/api/auth', authRouter);
app.use('/api/reminders', remindersRouter);
app.use('/api/dashboard', dashboardRouter);

const PORT = process.env.PORT || 5000;
const MONGO_URI = process.env.MONGO_URI;

async function start() {
  try {
    if (MONGO_URI) await mongoose.connect(MONGO_URI);
    app.listen(PORT, () => console.log(`Server running on ${PORT}`));
  } catch (err) {
    console.error(err);
    process.exit(1);
  }
}

start();
''',
'src/models/Reminder.js': '''import mongoose from 'mongoose';

const reminderSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: false },
  title: { type: String, required: true },
  type: { type: String, enum: ['time', 'loc', 'act', 'ai'], default: 'time' },
  scheduledAt: { type: Date },
  location: { type: String },
  enabled: { type: Boolean, default: true },
  done: { type: Boolean, default: false },
  meta: { type: Object, default: {} }
}, { timestamps: true });

export default mongoose.model('Reminder', reminderSchema);
''',
'src/models/User.js': '''import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true }
}, { timestamps: true });

export default mongoose.model('User', userSchema);
''',
'src/routes/auth.js': '''import { Router } from 'express';
import User from '../models/User.js';

const router = Router();

router.post('/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;
    const exists = await User.findOne({ email });
    if (exists) return res.status(400).json({ message: 'Email already exists' });
    const user = await User.create({ name, email, password });
    res.status(201).json({ id: user._id, name: user.name, email: user.email });
  } catch (e) {
    res.status(500).json({ message: e.message });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email, password });
    if (!user) return res.status(401).json({ message: 'Invalid credentials' });
    res.json({ id: user._id, name: user.name, email: user.email });
  } catch (e) {
    res.status(500).json({ message: e.message });
  }
});

export default router;
''',
'src/routes/reminders.js': '''import { Router } from 'express';
import Reminder from '../models/Reminder.js';

const router = Router();

router.get('/', async (req, res) => {
  const items = await Reminder.find().sort({ createdAt: -1 });
  res.json(items);
});

router.post('/', async (req, res) => {
  try {
    const item = await Reminder.create(req.body);
    res.status(201).json(item);
  } catch (e) {
    res.status(400).json({ message: e.message });
  }
});

router.patch('/:id', async (req, res) => {
  try {
    const item = await Reminder.findByIdAndUpdate(req.params.id, req.body, { new: true });
    res.json(item);
  } catch (e) {
    res.status(400).json({ message: e.message });
  }
});

router.patch('/:id/toggle', async (req, res) => {
  try {
    const current = await Reminder.findById(req.params.id);
    const item = await Reminder.findByIdAndUpdate(req.params.id, { enabled: !current.enabled }, { new: true });
    res.json(item);
  } catch (e) {
    res.status(400).json({ message: e.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    await Reminder.findByIdAndDelete(req.params.id);
    res.json({ message: 'Deleted' });
  } catch (e) {
    res.status(400).json({ message: e.message });
  }
});

export default router;
''',
'src/routes/dashboard.js': '''import { Router } from 'express';
import Reminder from '../models/Reminder.js';

const router = Router();

router.get('/', async (req, res) => {
  const total = await Reminder.countDocuments();
  const done = await Reminder.countDocuments({ done: true });
  const pending = total - done;
  const reminders = await Reminder.find().sort({ createdAt: -1 }).limit(5);
  res.json({ total, done, pending, reminders });
});

router.get('/stats', async (req, res) => {
  const total = await Reminder.countDocuments();
  const done = await Reminder.countDocuments({ done: true });
  const pending = total - done;
  res.json({ total, done, pending });
});

router.get('/ai-suggestions', async (req, res) => {
  res.json([
    { title: 'Check tyre pressure', type: 'loc', location: 'Petrol Pump' },
    { title: 'Buy medicine', type: 'time', scheduledAt: new Date() }
  ]);
});