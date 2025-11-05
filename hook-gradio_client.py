from PyInstaller.utils.hooks import collect_data_files

# 收集gradio_client的所有数据文件
datas = collect_data_files('gradio_client')

# 确保包含types.json文件
hiddenimports = ['gradio_client']