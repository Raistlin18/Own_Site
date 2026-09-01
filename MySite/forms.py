from django import forms


class ProductSearchForm(forms.Form):
    store = forms.ChoiceField(
        label="Store",
        choices=(
            ("newegg", "Newegg"),
            ("alza", "Alza"),
            ("emag", "eMAG"),
        ),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    product = forms.CharField(
        label="Product",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter a product name",
                "autocomplete": "off",
            }
        ),
    )

    def clean_product(self):
        return self.cleaned_data["product"].strip()
