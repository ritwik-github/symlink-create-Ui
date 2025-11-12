import sys
import os
import pathlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QFormLayout, 
    QLineEdit, QPushButton, QPlainTextEdit, QLabel,
    QHBoxLayout, QFileDialog, QStyle
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class SymlinkCreator(QWidget):
    """
    A simple PySide6 UI to create symbolic links (symlinks).
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        Initializes the user interface components.
        """
        self.setWindowTitle("openSym")
        self.setGeometry(300, 300, 1200, 400) # x, y, width, height

        # --- Layouts ---
        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- Get Standard Icons ---
        file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        save_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)

        # --- Widgets ---
        
        # Source Row
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Enter path or browse for file/folder")
        
        self.source_browse_file_btn = QPushButton()
        self.source_browse_file_btn.setIcon(file_icon)
        self.source_browse_file_btn.setToolTip("Browse for source file")

        self.source_browse_folder_btn = QPushButton()
        self.source_browse_folder_btn.setIcon(folder_icon)
        self.source_browse_folder_btn.setToolTip("Browse for source folder")

        source_layout = QHBoxLayout()
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(self.source_browse_file_btn)
        source_layout.addWidget(self.source_browse_folder_btn)
        
        # Destination Row
        self.dest_edit = QLineEdit()
        self.dest_edit.setPlaceholderText("Enter path or browse for destination")

        self.dest_browse_btn = QPushButton()
        self.dest_browse_btn.setIcon(save_icon)
        self.dest_browse_btn.setToolTip("Browse for destination symlink path")

        dest_layout = QHBoxLayout()
        dest_layout.setContentsMargins(0, 0, 0, 0)
        dest_layout.addWidget(self.dest_edit)
        dest_layout.addWidget(self.dest_browse_btn)

        self.proceed_btn = QPushButton("Create Symlink")
        
        self.log_widget = QPlainTextEdit()
        self.log_widget.setReadOnly(True)

        # --- Assemble Layout ---
        form_layout.addRow(QLabel("Source Path:"), source_layout)
        form_layout.addRow(QLabel("Destination Path:"), dest_layout)

        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.proceed_btn)
        main_layout.addWidget(QLabel("Log:"))
        main_layout.addWidget(self.log_widget)
        
        self.setLayout(main_layout)

        # --- Connections ---
        self.proceed_btn.clicked.connect(self.create_symlink)
        self.source_browse_file_btn.clicked.connect(self.browse_source_file)
        self.source_browse_folder_btn.clicked.connect(self.browse_source_folder)
        self.dest_browse_btn.clicked.connect(self.browse_dest)

        # --- Initial Log Message ---
        self.log("Welcome to Symlink Creator.")
        if os.name == 'nt':
            self.log("INFO: On Windows, this app may need to be 'Run as Administrator' to create symlinks.")

    def log(self, message):
        """
        Appends a message to the log widget.
        """
        self.log_widget.appendPlainText(message)

    def browse_source_file(self):
        """
        Opens a file dialog to select a source file.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Source File")
        if file_name:
            self.source_edit.setText(file_name)

    def browse_source_folder(self):
        """
        Opens a file dialog to select a source directory.
        """
        dir_name = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if dir_name:
            self.source_edit.setText(dir_name)

    def browse_dest(self):
        """
        Opens a file dialog to select a destination (save) path.
        """
        file_name, _ = QFileDialog.getSaveFileName(self, "Select Destination for Symlink")
        if file_name:
            self.dest_edit.setText(file_name)

    def create_symlink(self):
        """
        Backend logic to create the symbolic link.
        """
        source_path_str = self.source_edit.text().strip()
        dest_path_str = self.dest_edit.text().strip()

        # --- 1. Validation ---
        if not source_path_str or not dest_path_str:
            self.log("ERROR: Both Source and Destination paths are required.")
            return

        source_path = pathlib.Path(source_path_str)
        dest_path = pathlib.Path(dest_path_str)

        if not source_path.exists():
            self.log(f"ERROR: Source path does not exist: {source_path}")
            return

        if dest_path.exists() or dest_path.is_symlink():
            self.log(f"ERROR: Destination path already exists: {dest_path}")
            return

        # --- 2. Create Symlink ---
        try:
            self.log(f"Attempting to link: {dest_path} -> {source_path}")
            
            # Note: target_is_directory is only needed on Windows
            # for directory symlinks. We can check if the source is a dir.
            is_dir = source_path.is_dir()
            
            if os.name == 'nt':
                os.symlink(source_path, dest_path, target_is_directory=is_dir)
            else:
                # On POSIX (Linux/macOS), target_is_directory is not needed
                os.symlink(source_path, dest_path)

            self.log("----------------------------------")
            self.log(f"SUCCESS: Symlink created successfully.")
            self.log(f"  Source: {source_path}")
            self.log(f"  Link:   {dest_path}")
            self.log("----------------------------------")

        except OSError as e:
            self.log(f"ERROR: Could not create symlink.")
            self.log(f"  Details: {e}")
            if os.name == 'nt' and e.winerror == 1314:
                 self.log("  This is a permissions error. Please try running this application as an Administrator.")
        except Exception as e:
            self.log(f"ERROR: An unexpected error occurred: {e}")


def main():
    """
    Main function to run the application.
    """
    app = QApplication(sys.argv)
    window = SymlinkCreator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

