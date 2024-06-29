# Python Package to Display Stats from an EC3 Save File

> [!NOTE]
> Work in progress!

> [!CAUTION]
> Backup your save file.  If the game writes when this module is trying to read then irrecoverable file corruption can occur.

> [!TIP]
> You will need to obtain a password in order to decrypt the save file. No functionality is provided to edit the save file, this is a fancy viewer only.

![Most common ghosts](assets/common_ghosts.png)
![Most played maps](assets/played_maps.png)

To build the exe run:

```shell
pyinstaller -n statsaphobia.exe --onefile run.py
```
