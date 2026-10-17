# Challenge submission form — ready-to-paste answers

## Challenge

Select the closest available challenge category to **Artificial Intelligence / Computer Vision / Smart Cities / Transportation / Sustainability**. If the form provides a road-safety or infrastructure option, choose that.

## What is the Problem you are trying to solve?

Potholes are a common road-safety and maintenance problem. They can damage vehicles, cause accidents, slow traffic, and increase repair costs. Today, pothole reporting is often manual, subjective, and delayed. Municipal teams need a faster way to identify potholes from road images so that inspections can be prioritized and repairs can be planned using evidence. The project solves this problem by automatically detecting visible potholes in images and video and returning their location, confidence score, and annotated evidence frame. The system is an inspection-support tool, not a replacement for engineering measurement or a final repair decision.

## How are you planning to solve the problem? (Brief Overview)

We will build a one-class object-detection model using a pretrained YOLO model and transfer learning. The training pipeline downloads the official RDD2022 India road-damage data, converts its Pascal VOC XML annotations into YOLO format, retains the D40 pothole class, and creates reproducible train and validation splits. The Jupyter notebook trains the model, validates it using precision, recall, mAP50, and mAP50-95, plots sample predictions, and runs inference on new images, videos, or webcam frames. The output is an annotated frame with bounding boxes and confidence scores. A lightweight Linux deployment can later process survey-vehicle or smartphone video and export detections to a CSV or GIS workflow. Data augmentation and confidence/NMS thresholds help improve robustness, while a held-out local sample should be used before operational deployment.

## How does your solution leverage IBM Z / LinuxONE technologies?

The solution is packaged as a reproducible Python and Jupyter workflow for LinuxONE. LinuxONE provides a secure, enterprise Linux environment in which the dataset preparation, model training, validation, and inference steps can run consistently and be integrated with existing municipal or enterprise data systems. Python, JupyterLab, OpenCV, and Ultralytics YOLO provide the application layer, while Linux containers or virtual environments make dependencies repeatable. The trained model can be run as a batch inspection service on LinuxONE: images or video frames are ingested, detections are generated, and results are written to an auditable CSV/object store or passed to a maintenance workflow. LinuxONE’s enterprise security, centralized operations, scalability, and high availability are relevant when multiple inspection teams or cities submit road imagery. The prototype does not claim a proprietary IBM accelerator; it demonstrates a Linux-native workload that can be containerized and operationalized on IBM Z/LinuxONE.

## What value does your solution deliver, and who will benefit from it?

The primary beneficiaries are municipal road authorities, public-works inspection teams, transport agencies, and road-maintenance contractors. Drivers and pedestrians benefit indirectly from faster identification and prioritization of hazardous road defects. The solution reduces manual screening time, creates consistent evidence for work orders, and helps teams focus field inspections on locations with the highest predicted risk. It can support a scalable survey process using existing smartphone or vehicle cameras rather than requiring specialized hardware. The main outcome is a ranked, reviewable set of pothole detections with visual evidence, not an unsupported promise of fully automatic repair decisions. Success should be measured on a local held-out set using recall, precision, false positives per kilometer or frame, processing speed, and the time from image capture to a maintenance-ready report.

## Upload your pitch deck in PDF format

Upload `docs/pitch_deck.pdf` from this project package. It is intentionally concise and should remain under the form’s 5 MB limit.

## GitHub Link of your Project / Link of your Zip File

After publishing the folder as a public GitHub repository or uploading the ZIP, paste that public URL here. Example format: `https://github.com/<your-username>/AI_Potholes_Detection`

## Video Submission Link

Record a public or unlisted 2–3 minute video showing: the problem, the notebook setup, dataset conversion, training output, validation metrics, and a live prediction on an image or video. Paste the YouTube/Vimeo URL here. Do not paste a local file path.

## Share the link to your pitch deck in PDF format (if not able to upload the file)

If the upload succeeds, leave this blank. If it fails, upload `docs/pitch_deck.pdf` to a public read-only location such as a GitHub release or cloud drive and paste the share URL. Test it in a private/incognito window before submitting.

## Link to all open-source resources used

https://github.com/sekilab/RoadDamageDetector; https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547; https://sites.google.com/view/pothole-600/dataset; https://docs.ultralytics.com/usage/python/; https://github.com/ultralytics/ultralytics; https://opencv.org/; https://jupyter.org/

## Final upload checklist

- Upload `docs/pitch_deck.pdf`.
- Publish the project ZIP or GitHub repository publicly.
- Replace the GitHub placeholder with the real public URL.
- Add the final public video URL.
- Keep the dataset download instructions and citations in the repository, but avoid committing a multi-hundred-megabyte dataset archive unless its terms explicitly allow redistribution.
- Run the notebook once and include a screenshot of a successful annotated prediction in the video or repository README.
