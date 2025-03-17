from cvzone.HandTrackingModule import HandDetector
import cv2
import os
import time

# Parameters
width, height = 1280, 720  # Screen resolution
gestureThreshold = 300
folderPath = "Presentation"

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Hand Detector
detectorHand = HandDetector(detectionCon=0.8, maxHands=1)

# Variables
imgList = []
buttonPressed = False
gestureControl = False  # Toggle for gesture control
imgNumber = 0
annotations = [[]]
annotationNumber = -1
annotationStart = False
hs, ws = int(120 * 1), int(213 * 1)  # Small image size
zoomLevel = 1  # Zoom level
lastGestureTime = 0  # Timestamp for last gesture
gestureCooldown = 10  # Cooldown time (in seconds)

# Get list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

while True:
    # Get image frame
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)
    imgCurrent = cv2.resize(imgCurrent, (width, height))

    # Apply zoom
    if zoomLevel != 1:
        h, w, _ = imgCurrent.shape
        newH, newW = int(h * zoomLevel), int(w * zoomLevel)
        imgCurrent = cv2.resize(imgCurrent, (newW, newH))
        startX, startY = (newW - width) // 2, (newH - height) // 2
        imgCurrent = imgCurrent[startY:startY + height, startX:startX + width]

    # Find the hand and its landmarks
    hands, img = detectorHand.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands:
        hand = hands[0]
        cx, cy = hand["center"]
        fingers = detectorHand.fingersUp(hand)

        # Toggle Gesture Control (Open Palm 🖐️)
        if fingers == [1, 1, 1, 1, 1]:
            if time.time() - lastGestureTime >= gestureCooldown:
                gestureControl = not gestureControl
                print(f"Gesture Control: {'ON' if gestureControl else 'OFF'}")
                lastGestureTime = time.time()  # Reset cooldown

        if gestureControl and not buttonPressed and (time.time() - lastGestureTime >= gestureCooldown):
            # Left Swipe (Thumb Up 👍)
            if fingers == [1, 0, 0, 0, 0]:
                print("Left")
                buttonPressed = True
                if imgNumber > 0:
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                lastGestureTime = time.time()  # Reset cooldown

            # Right Swipe (Pinky Up 👎)
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                buttonPressed = True
                if imgNumber < len(pathImages) - 1:
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = -1
                    annotationStart = False
                lastGestureTime = time.time()  # Reset cooldown

            # Draw Mode (Index + Middle Finger ☝️✌️)
            if fingers == [0, 1, 1, 0, 0]:
                cv2.circle(imgCurrent, (cx, cy), 12, (0, 0, 255), cv2.FILLED)

            # Start Annotation (Index Finger ☝️)
            if fingers == [0, 1, 0, 0, 0]:
                if not annotationStart:
                    annotationStart = True
                    annotationNumber += 1
                    annotations.append([])
                annotations[annotationNumber].append((cx, cy))
                cv2.circle(imgCurrent, (cx, cy), 12, (0, 0, 255), cv2.FILLED)
            else:
                annotationStart = False

            # Undo Last Annotation (Three Fingers ☝️✌️🤞)
            if fingers == [0, 1, 1, 1, 0]:
                if annotations:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True
                lastGestureTime = time.time()

            # Clear All Annotations (Pinch 🤏)
            if fingers == [1, 1, 0, 0, 0]:
                annotations = [[]]
                annotationNumber = -1
                print("Clear All Annotations")
                lastGestureTime = time.time()

            # Zoom In (Closed Fist ✊)
            if fingers == [0, 0, 0, 0, 0]:
                zoomLevel = min(zoomLevel + 0.1, 2)
                print(f"Zoom In: {zoomLevel}")
                lastGestureTime = time.time()

            # Zoom Out (Thumb + Pinky ☝️👆)
            if fingers == [1, 0, 0, 0, 1]:
                zoomLevel = max(zoomLevel - 0.1, 1)
                print(f"Zoom Out: {zoomLevel}")
                lastGestureTime = time.time()

    if buttonPressed:
        buttonPressed = False  # Reset button press flag

    # Draw Annotations
    for annotation in annotations:
        for j in range(len(annotation)):
            if j != 0:
                cv2.line(imgCurrent, annotation[j - 1], annotation[j], (0, 0, 200), 12)

    # Overlay Camera Feed on Presentation
    imgSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w - ws: w] = imgSmall

    # Display Images
    cv2.imshow("Slides", imgCurrent)
    cv2.imshow("Image", img)

    # Quit with 'q'
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
