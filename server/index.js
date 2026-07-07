import express from "express";
import cors from "cors";
import multer from "multer";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import { parse } from "csv-parse/sync";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const AI_DOC_ASSISTANT_DIR = path.join(__dirname, "..", "ai_doc_assistant");
const UPLOAD_DIR = path.join(AI_DOC_ASSISTANT_DIR, "inbox");
const RESULT_DIR = path.join(AI_DOC_ASSISTANT_DIR, "outputs");
const CSV_PATH = path.join(RESULT_DIR, "results.csv");
const SUMMARIES_DIR = path.join(RESULT_DIR, "summaries");

fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    cb(null, `${unique}-${file.originalname}`);
  },
});

const upload = multer({ storage });

const app = express();
app.use(cors());

app.post("/api/upload", upload.single("file"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "No file uploaded" });
  }
  res.json({
    message: "File uploaded successfully",
    filename: req.file.filename,
    size: req.file.size,
  });
});

app.get("/api/results", (req, res) => {
  if (!fs.existsSync(CSV_PATH)) {
    return res.json({ columns: [], rows: [] });
  }
  const content = fs.readFileSync(CSV_PATH, "utf-8");
  const rows = parse(content, { columns: true, skip_empty_lines: true });
  const columns = rows.length > 0 ? Object.keys(rows[0]) : [];
  res.json({ columns, rows });
});

app.get("/api/latest-summary", (req, res) => {
  if (!fs.existsSync(SUMMARIES_DIR)) {
    return res.json({ filename: null, content: "" });
  }
  const files = fs
    .readdirSync(SUMMARIES_DIR)
    .map((name) => ({
      name,
      mtime: fs.statSync(path.join(SUMMARIES_DIR, name)).mtimeMs,
    }))
    .sort((a, b) => b.mtime - a.mtime);

  if (files.length === 0) {
    return res.json({ filename: null, content: "" });
  }

  const latest = files[0].name;
  const content = fs.readFileSync(path.join(SUMMARIES_DIR, latest), "utf-8");
  res.json({ filename: latest, content });
});

const PORT = 4000;
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`Storing uploads in: ${UPLOAD_DIR}`);
});
