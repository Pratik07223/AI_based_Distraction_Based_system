# Focus Guard AI

Focus Guard AI is a Python desktop application that uses a webcam to estimate whether a user is focused, distracted, or using a phone. It combines a TensorFlow image classifier with MediaPipe eye tracking and optional YOLO phone detection. The live view shows the current status and rolling focus/phone scores. It can also issue spoken and beep alerts, save screenshots, and send critical alerts through Telegram.

> This is a learning project and its predictions can be wrong. Use it as an attention aid, not as a safety-critical monitoring system.

## Features

- Classifies webcam frames as `focused`, `distracted`, or `phone` using a MobileNetV2-based Keras model.
- Estimates eye state and gaze direction with MediaPipe Face Mesh.
- Detects phones with the YOLOv8 COCO model when the optional detector is available.
- Smooths predictions over recent frames and displays status, focus score, phone score, distraction score, and FPS.
- Provides timed voice/beep alerts; at the critical alert stage it can save a frame and send Telegram text/photo messages.
- Includes scripts to capture, clean, split, and train image data.

## Requirements

- Windows (the sound alert module uses `winsound`), Python 3.10, and a working webcam.
- The trained model at `models/attention_model.h5` is required to run the app.
- The phone detector loads `yolov8n.pt` from the project root. If YOLO or its weights are unavailable, the app attempts to continue without phone detection.
- TensorFlow 2.10 is pinned in `requirements.txt`; it is intended for the project's Python 3.10 environment. Installing it may require a compatible Python/platform setup.

The checked-in `requirements.txt` covers some core packages but does not list every library imported by the app and scripts. In particular, eye tracking needs `mediapipe` and `scipy`; the training script needs `scikit-learn`, `matplotlib`, and `seaborn`; and the cleanup/build scripts need `imagehash` and `icrawler`. Install any missing packages in the active environment before using those features. The TensorFlow and PyTorch/Ultralytics dependencies can be large.

## Setup

From the project directory in PowerShell:

```powershell
py -3.10 -m venv venv310
.\venv310\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install mediapipe scipy scikit-learn matplotlib seaborn imagehash icrawler
```

If PowerShell blocks activation, use `venv310\Scripts\python.exe` directly in place of `python` and `venv310\Scripts\pip.exe` in place of `pip`.

Check that these files exist before starting:

```text
models/attention_model.h5
yolov8n.pt
```

## Run the application

```powershell
python main.py
```

Allow camera access if Windows asks. Press **Esc** in the video window to exit. The app writes session status lines to `output_log.txt`; critical alert screenshots are stored in `alerts/`.

`main.py` is the current feature-rich entry point.
## Alerts and privacy

- Voice alerts use `pyttsx3` and the system's installed voices. The main app defaults to English; the `LANG` setting in `main.py` can be changed to `"hi"` for Hindi prompts when a Hindi system voice is available.
- On Windows, sound alerts use `winsound`.
- The main app currently enables Telegram alerts and screenshots in `main.py`. Telegram configuration is currently stored as constants in `app/alerts/telegram_alert.py`. Set these to your own bot token and chat ID before enabling Telegram, and never commit credentials. A Telegram credential has been present in the source; revoke/rotate it with BotFather before using this integration.
- Camera frames are processed locally during normal operation. When Telegram alerts are enabled, a critical alert screenshot is saved locally and sent to the configured Telegram chat.

## Dataset and model workflow

The dataset uses one directory per class:

```text
dataset/
  focused/
  distracted/
  phone/
```

To capture examples from the webcam, set `label` in `scripts/capture_data.py` to one of those class names and run:

```powershell
python scripts/capture_data.py
```

Press **S** to save a frame and **Q** to quit. Captures are written into the matching `dataset/<label>/` folder.

The included scripts have distinct roles:

| Script | Purpose |
|---|---|
| `scripts/capture_data.py` | Capture labeled webcam frames. |
| `scripts/build_dataset.py` | Download example images, remove invalid/small images, filter for faces, and balance classes. Uses `icrawler`; downloading images has separate source and usage rights to consider. |
| `scripts/clean_dataset.py` | Remove invalid, blurry, and perceptually duplicated images from `dataset/`. |
| `scripts/remove_duplicates.py` | Remove byte-identical duplicates in the three class folders. |
| `scripts/split_dataset.py` | Copy images into an 80/20 `dataset_clean/train` and `dataset_clean/val` split. |
| `scripts/train_model.py` | Fine-tune MobileNetV2, evaluate it, and save `models/attention_model.h5`. |

A typical flow for preparing your own model is:

```powershell
python scripts/capture_data.py
python scripts/clean_dataset.py
python scripts/split_dataset.py
python scripts/train_model.py
```

`build_dataset.py` is an alternative image collection path. `remove_duplicates.py` is an additional exact-duplicate cleanup step. Review scripts before running them: cleaning scripts delete files from `dataset/`, and `split_dataset.py` copies into existing `dataset_clean/` folders without clearing them first. Back up your images and clear old split folders manually when you want a fresh split.

The training script saves a categorical classifier in `models/attention_model.h5`. At inference, `app/detection/predict_attention.py` maps output indices in this order: `distracted`, `focused`, `phone`. Keep this mapping aligned with the training class order if you change classes or training data.

## Project structure

```text
app/
  alerts/       Voice, beep, and Telegram notification helpers
  detection/    Attention classifier and YOLO phone detector
  utils/        Alert screenshot saving
  vision/       Eye tracking and face cropping helpers
scripts/        Data capture, preparation, splitting, and training
models/         Trained attention classifier
dataset/        Labeled source images
dataset_clean/  Train/validation images used by training
alerts/         Screenshots generated by critical alerts
main.py         Main live webcam application
requirements.txt
```

## Troubleshooting

- **Camera window does not open:** Check that the webcam is connected and not being used by another app. The application opens camera index `0` by default.
- **Model file error:** Confirm `models/attention_model.h5` exists and can be loaded by the installed TensorFlow version.
- **MediaPipe import or `solutions` error:** Confirm the intended Python 3.10 virtual environment is active and install a compatible `mediapipe` package.
- **YOLO import/weights error:** Install `ultralytics` and ensure `yolov8n.pt` is in the project root. Phone detection is optional in `main.py`.
- **No Telegram message:** Verify the bot token and chat ID in `app/alerts/telegram_alert.py`, ensure the bot can message that chat, and check network access.
- **No sound:** Check Windows audio and confirm the process is running on Windows.

## License

No license file is currently included. Add a license before redistributing the project.


