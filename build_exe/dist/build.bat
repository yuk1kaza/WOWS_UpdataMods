@echo off
setlocal enabledelayedexpansion

:: 使用绝对路径并添加引号
set "PROJECT_ROOT=D:\Programs\pycharm\build_exe"
set "VENV_ACTIVATE=!PROJECT_ROOT!\.venv\Scripts\activate.bat"
set "SCRIPT=!PROJECT_ROOT!\src\voice_tool.py"

:: 显示路径验证
echo 正在验证路径...
if not exist "!VENV_ACTIVATE!" (
    echo 错误：找不到虚拟环境激活脚本
    goto error
)
if not exist "!SCRIPT!" (
    echo 错误：找不到Python脚本文件
    goto error
)

:: 激活虚拟环境
echo 正在激活虚拟环境...
call "!VENV_ACTIVATE!"

:: 检查PyInstaller是否安装
where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo 正在安装PyInstaller...
    pip install pyinstaller==6.7.0
)

:: 执行打包命令
echo 开始打包...
pyinstaller --noconfirm ^
--onefile ^
--noconsole ^
--name "VoiceTool" ^
--distpath "!PROJECT_ROOT!\dist" ^
--workpath "!PROJECT_ROOT!\build" ^
--hidden-import tkinter ^
--clean ^
"!SCRIPT!"

echo 打包完成！
goto end

:error
echo 发生错误，请检查上述提示
pause
exit /b 1

:end
pause