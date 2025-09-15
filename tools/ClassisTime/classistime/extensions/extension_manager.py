#!/usr/bin/env python3
"""
Extension manager for ClassisTime application
"""

import os
import sys
import json
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

class ExtensionManager(QObject):
    """Manages extensions for ClassisTime"""
    
    extension_installed = pyqtSignal(str)  # extension name
    extension_removed = pyqtSignal(str)    # extension name
    extension_updated = pyqtSignal(str)    # extension name
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.extensions_dir = Path.home() / '.classistime' / 'extensions'
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        self.extensions: Dict[str, dict] = {}
        self.load_extensions()
        
    def load_extensions(self):
        """Load all installed extensions"""
        self.extensions = {}
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir():
                manifest_path = ext_dir / 'manifest.json'
                if manifest_path.exists():
                    try:
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                            self.extensions[manifest['name']] = {
                                'manifest': manifest,
                                'path': ext_dir
                            }
                    except Exception as e:
                        print(f"Error loading extension {ext_dir.name}: {e}")
                        
    def install_extension(self, zip_path: str) -> bool:
        """Install extension from zip file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Check if manifest.json exists
                if 'manifest.json' not in zip_ref.namelist():
                    raise ValueError("Missing manifest.json in extension package")
                
                # Extract extension to temporary directory
                temp_dir = self.extensions_dir / 'temp_install'
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                temp_dir.mkdir()
                
                zip_ref.extractall(temp_dir)
                
                # Read manifest
                manifest_path = temp_dir / 'manifest.json'
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest = json.load(f)
                
                # Check if extension already exists
                ext_name = manifest['name']
                ext_dir = self.extensions_dir / ext_name
                
                if ext_name in self.extensions:
                    # Update existing extension
                    if ext_dir.exists():
                        shutil.rmtree(ext_dir)
                    shutil.move(str(temp_dir), str(ext_dir))
                    self.extensions[ext_name] = {
                        'manifest': manifest,
                        'path': ext_dir
                    }
                    self.extension_updated.emit(ext_name)
                else:
                    # New installation
                    shutil.move(str(temp_dir), str(ext_dir))
                    self.extensions[ext_name] = {
                        'manifest': manifest,
                        'path': ext_dir
                    }
                    self.extension_installed.emit(ext_name)
                
                return True
        except Exception as e:
            error_msg = f"Failed to install extension: {str(e)}"
            print(error_msg)
            QMessageBox.critical(None, "安装失败", error_msg)
            return False
            
    def remove_extension(self, ext_name: str) -> bool:
        """Remove an installed extension"""
        if ext_name not in self.extensions:
            return False
            
        try:
            ext_path = self.extensions[ext_name]['path']
            if ext_path.exists():
                shutil.rmtree(ext_path)
            del self.extensions[ext_name]
            self.extension_removed.emit(ext_name)
            return True
        except Exception as e:
            error_msg = f"Failed to remove extension: {str(e)}"
            print(error_msg)
            QMessageBox.critical(None, "卸载失败", error_msg)
            return False
            
    def get_extension_info(self, ext_name: str) -> Optional[dict]:
        """Get extension information"""
        return self.extensions.get(ext_name)
        
    def list_extensions(self) -> List[dict]:
        """List all installed extensions"""
        return [ext_info for ext_info in self.extensions.values()]
        
    def load_extension_module(self, ext_name: str):
        """Load and return extension module"""
        if ext_name not in self.extensions:
            return None
            
        ext_path = self.extensions[ext_name]['path']
        module_path = ext_path / 'main.py'
        
        if not module_path.exists():
            return None
            
        # Add extension directory to Python path
        sys.path.insert(0, str(ext_path))
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(ext_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading extension module {ext_name}: {e}")
            return None
        finally:
            # Remove from Python path
            if str(ext_path) in sys.path:
                sys.path.remove(str(ext_path))