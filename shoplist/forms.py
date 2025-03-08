from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class DateInput(forms.DateInput):
    input_type = 'date'


class NewSessionForm(forms.Form):
    sale_date = forms.DateField(widget=DateInput)
    images = MultipleFileField(required=False)


class AddPhotoForm(forms.Form):
    images = MultipleFileField(required=False)
