from django.forms import ModelForm
from .models import Inventory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AddInventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'cost_per_item', 'quantity_in_stock', 'quantity_sold', 'location']
        
class UpdateInventoryForm(ModelForm):
    class Meta:
        model = Inventory
        fields = ['name', 'cost_per_item', 'quantity_in_stock', 'quantity_sold', 'location']

class AddUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', )