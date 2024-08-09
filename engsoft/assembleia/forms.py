from django import forms
from .models import Assembleia
from login.models import Construtora, Condominio

class AssembleiaForm(forms.ModelForm):
    class Meta:
        model = Assembleia
        fields = ['condominio','titulo', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            try:
                construtora = Construtora.objects.get(administrador=user)
                condominios = Condominio.objects.filter(construtora=construtora)
            except Construtora.DoesNotExist:
                condominios = Condominio.objects.none()  # Se não houver construtora, não mostra condomínios
            
            self.fields['condominio'].queryset = condominios
