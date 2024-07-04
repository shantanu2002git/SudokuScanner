## Features
Image Capture: Capture an image of a Sudoku puzzle using your webcam.
Image Upload: Upload an existing image of a Sudoku puzzle.
OCR Text Extraction: Extract the numbers from the Sudoku puzzle image using Tesseract OCR.
Sudoku Solving: Automatically solve the Sudoku puzzle using a backtracking algorithm.
Editing: Manually edit the Sudoku grid by inserting numbers.
Undo/Redo: Undo and redo changes made to the Sudoku grid.
Progress Saving/Loading: Save and load the current state of the Sudoku puzzle.
Hint: Get a hint for the next empty cell in the Sudoku grid.
Theme Switching: Switch between light and dark themes.

## You can install the required packages using pip:
pip install opencv-python pytesseract pillow tkinter tkinterdnd2

## Usage
1. Run the sudoku_ocr_scanner.py script to start the application.
2. Use the "Capture Image" or "Upload Photo" button to get an image of the Sudoku puzzle.
3. The application will automatically extract the numbers from the image and display them in the Sudoku grid.
4. You can manually edit the Sudoku grid by clicking on the cells and entering numbers.
5. Click the "Submit" button to solve the Sudoku puzzle.
6. Use the "Undo" and "Redo" buttons to manage your changes.
7. Click the "Save Progress" button to save the current state of the Sudoku puzzle, and the "Load Progress" button to load a previously saved puzzle.
8. Use the "Hint" button to get a hint for the next empty cell.
9. Click the "Switch Theme" button to toggle between light and dark themes.[ work on it ... ]

## Contributing
If you find any issues or have suggestions for improvements, feel free to create a new issue or submit a pull request on the GitHub repository.

## License
This project is licensed under the MIT License.
