# NovaBank Angel — Subir a GitHub y desplegar desde ahí

El código ya está clonado desde Hugging Face y preparado con el workflow de sincronización.

## 1. Crear el repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new).
2. **Repository name:** `NovaBank_Angel` (o el que prefieras, ej. `novabank-angel-demo`).
3. **Visibility:** Public (o Private).
4. **No** marques "Add a README" (el repo debe estar vacío para hacer el primer push).
5. Clic en **Create repository**.

## 2. Subir el código desde tu PC

En PowerShell (ajusta el nombre del repo si usaste otro):

```powershell
cd C:\Users\Angel\NovaBank_Angel
git push -u origin main
```

Si creaste el repo con otro nombre (ej. `novabank-angel-demo`), actualiza el remote antes:

```powershell
git remote set-url origin https://github.com/angelucv/NOMBRE_QUE_ELEGISTE.git
git push -u origin main
```

## 3. Sincronización automática con Hugging Face

En el repo de GitHub: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- **Name:** `HF_TOKEN`
- **Secret:** tu token de Hugging Face (permiso **Write**), desde [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).

A partir de ahí, cada **push a `main`** actualizará el Space [angelucv/NovaBank_Angel](https://huggingface.co/spaces/angelucv/NovaBank_Angel).

## Remotes actuales

- `origin` → GitHub (tu nuevo repo)
- `hf` → Hugging Face Space (para push manual si quieres: `git push hf main`)
