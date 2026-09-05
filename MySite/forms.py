from django import forms


class ProductSearchForm(forms.Form):
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
