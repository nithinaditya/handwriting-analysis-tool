const PORT = 3002;
let pdfName = ''
let filename = ''
let jsonData = null
let grade=''
let url = ''
let message = ''
let keys = ''
let finalPdfName=''
//importing dependencies
const express = require("express");
const path = require("path");
const fs = require("fs");
const {spawn} = require('child_process');

//pdf merger
const PDFMerger = require('pdf-merger-js');


//initializing the app
const app = express();

//initializing the multer
const multer = require("multer");

// initializing the pdf merger
var merger = new PDFMerger();


//configuring the multer storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "upload_images");
  },
  filename: (req, file, cb) => {
    filename = file.originalname;
    cb(null, file.originalname);
  },
});

const upload = multer({ storage: storage });

//middleware------------------
app.use("/assets", express.static(path.join(__dirname, "assets")));
app.use(express.json());
app.set("view engine", "ejs");

//routes-starting-------------
//home route
app.get("/", (req, res) => {
  res.status(200).render("home");
});

//task route
app.get("/task", (req, res) => {
  res.status(200).render("task", {
    upload: "",
  });
});

//uploading the image
app.post("/upload", upload.single("image"), (req, res) => {
  let dataToSend = ''
  console.log(filename);
    const python = spawn('python', ['script01.py', filename ]);
    python.stdout.on('data', function (data) {
      console.log('Pipe data from python script ...');
      console.log(jsonData);
      jsonData = JSON.parse(data);
        });
     
     // in close event we are sure that stream from child process is closed
     python.on('close', (code) => {
     console.log(`child process close all stdio with code ${code}`);
     // send data to browser
      filename=''
      grade = jsonData['grade'];
      message = jsonData['message']
      delete jsonData.grade;
      delete jsonData.message;
      url = `./assets/images/${grade}-grade.png`

      //making the pdf
      keys = Object.keys(jsonData)
      len = keys.length
      for(i=0;i<len;i++){
        merger.add(`./assets/example/${keys[i]}.pdf`);
        pdfName = pdfName + `${keys[i]}`
      }

      finalPdfName = pdfName;
      pdfName='';

      (async () => {
        await merger.save(`${finalPdfName}.pdf`); //save under given name and reset the internal document
      })();
      res.status(200).render('result',{
        url : url,
        message : message,
        keys: keys
      })
     });
});

//about nav-bar
app.get('/about',(req, res)=>{
  res.status(200).render('about')
})

//result route

app.get('/result',(req, res)=>{
  res.status(200).render('result')
})

//sending pdf to the user
app.get("/pdf", (req, res) => {
  var data = fs.readFileSync(`${finalPdfName}.pdf`);
  res.contentType("application/pdf");
  pdfName='';
  res.send(data);
});


//other routes sending error 404 page
app.use("*", (req, res) => {
  res.status(404).render('404');
});

app.listen(PORT, () => {
  console.log("server running at port 3002");
});
