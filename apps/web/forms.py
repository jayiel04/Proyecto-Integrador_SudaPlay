import io
import zipfile

from django import forms

from .models import Game


class GameForm(forms.ModelForm):
    # Campos de archivo como FileField independientes (no del modelo, que ya es URLField)
    cover_image_file = forms.ImageField(
        label="Imagen de portada",
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
    )
    game_file_upload = forms.FileField(
        label="Archivo del juego (.zip con index.html)",
        required=False,
        widget=forms.ClearableFileInput(attrs={"accept": ".zip"}),
    )

    class Meta:
        model = Game
        fields = [
            "title",
            "short_description",
            "description",
            "genre",
            "external_url",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "short_description": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        game_file = cleaned_data.get("game_file_upload")
        external_url = cleaned_data.get("external_url")

        if not game_file and not external_url:
            raise forms.ValidationError("Debes subir un archivo ZIP o proporcionar un enlace externo.")

        if game_file:
            if not game_file.name.lower().endswith(".zip"):
                raise forms.ValidationError("El archivo del juego debe ser un .zip.")

            try:
                game_file.seek(0)
                with zipfile.ZipFile(io.BytesIO(game_file.read())) as zf:
                    names = [n.lower() for n in zf.namelist()]
                    if not any(n.endswith("index.html") for n in names):
                        raise forms.ValidationError("El ZIP debe incluir un archivo index.html.")
            except zipfile.BadZipFile:
                raise forms.ValidationError("El archivo subido no es un ZIP válido.")
            finally:
                game_file.seek(0)

        return cleaned_data


class PerfilForm(forms.Form):
    avatar = forms.ImageField(required=True)