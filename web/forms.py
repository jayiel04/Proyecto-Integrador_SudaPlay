from django import forms
import zipfile

from .models import Game


class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = [
            "title",
            "short_description",
            "description",
            "genre",
            "cover_image",
            "external_url",
            "game_file",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "short_description": forms.Textarea(attrs={"rows": 2}),
            "game_file": forms.ClearableFileInput(attrs={"accept": ".zip"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        game_file = cleaned_data.get("game_file")
        external_url = cleaned_data.get("external_url")

        if not game_file and not external_url:
            raise forms.ValidationError("Debes subir un archivo o proporcionar un enlace externo.")

        if game_file:
            file_name = game_file.name.lower()
            if not file_name.endswith(".zip"):
                raise forms.ValidationError("Para jugar dentro de la plataforma, el archivo debe ser .zip.")

            try:
                with zipfile.ZipFile(game_file) as zip_file:
                    names = [name.lower() for name in zip_file.namelist()]
                    has_index = any(name.endswith("index.html") for name in names)
                    if not has_index:
                        raise forms.ValidationError("El ZIP debe incluir un archivo index.html.")
            except zipfile.BadZipFile:
                raise forms.ValidationError("El archivo subido no es un ZIP valido.")
            finally:
                game_file.seek(0)

        return cleaned_data
