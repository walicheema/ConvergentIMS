from django.shortcuts import get_object_or_404, render, redirect
from .models import Inventory
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AddInventoryForm, UpdateInventoryForm, AddUserForm
from django.contrib import messages
from django_pandas.io import read_frame
import plotly
import plotly.express as px
import json

@login_required
def inventory_list(request):
    inventories = Inventory.objects.all()
    context = {
        "inventories": inventories
    }
    return render(request, "inventory/inventory_list.html", context=context)

@login_required
def per_product_view(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    context = {
        'inventory': inventory
    }
    
    return render(request, "inventory/per_product.html", context=context)

@login_required
def add_product(request):
    if request.method == "POST":
        add_form = AddInventoryForm(data=request.POST)
        if add_form.is_valid():
            new_inventory = add_form.save(commit=False)
            new_inventory.sales = float(add_form.data['cost_per_item']) * float(add_form.data['quantity_sold'])
            new_inventory.location = add_form.data['location']
            new_inventory.save()
            messages.success(request, "Successfully Added Product")
            return redirect("/inventory/")
    else:
        add_form = AddInventoryForm()
    
    return render(request, "inventory/inventory_add.html", {"form": add_form})

@login_required
def delete_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    inventory.delete()
    messages.success(request, "Inventory Deleted")
    return redirect("/inventory/")

@login_required
def update_inventory(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == "POST":
        updateForm = UpdateInventoryForm(data=request.POST)
        if updateForm.is_valid():
            inventory.name = updateForm.data['name']
            inventory.quantity_in_stock = updateForm.data['quantity_in_stock']
            inventory.quantity_sold = updateForm.data['quantity_sold']
            inventory.cost_per_item = updateForm.data['cost_per_item']
            inventory.sales = float(inventory.cost_per_item) * float(inventory.quantity_sold)
            inventory.location = updateForm.data['location']
            inventory.save()
            messages.success(request, "Inventory Updated")
            return redirect(f"/inventory/per_product/{pk}")
    
    else:
        updateForm = UpdateInventoryForm(instance=inventory)
    context = {"form": updateForm}
    return render(request, "inventory/inventory_update.html", context=context)

@login_required
def add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('inventory_list')
    else:
        form = AddUserForm()
    return render(request, 'inventory/add_user.html', {'form': form})

@login_required
def dashboard(request):
    inventories = Inventory.objects.all()
    
    df = read_frame(inventories)
    
    print(df.columns)
    sales_graph_df = df.groupby(by="last_sales_date", as_index=False, sort=False)['sales'].sum()
    print(sales_graph_df.sales)
    print(sales_graph_df.columns)
    sales_graph = px.line(sales_graph_df, x=sales_graph_df.last_sales_date, y=sales_graph_df.sales, title="Sales Trend")
    sales_graph = json.dumps(sales_graph, cls=plotly.utils.PlotlyJSONEncoder)
    
    best_performing_product_df = df.groupby(by="name").sum().sort_values(by="quantity_sold")
    best_performing_product = px.bar(best_performing_product_df,                            
                                     x = best_performing_product_df. index,
                                     y = best_performing_product_df.quantity_sold,
                                     title = "Best Performing Products"
                                     )
    best_performing_product = json.dumps(best_performing_product, cls=plotly.utils.PlotlyJSONEncoder)
    
    most_product_in_stock_df = df.groupby(by="name").sum().sort_values(by="quantity_in_stock")
    most_product_in_stock = px.pie(most_product_in_stock_df,                            
                                     names = most_product_in_stock_df.index,
                                     values = most_product_in_stock_df.quantity_sold,
                                     title = "Highest Stock"
                                     )
    most_product_in_stock = json.dumps(most_product_in_stock, cls=plotly.utils.PlotlyJSONEncoder)
    
    context = {
        "sales_graph": sales_graph,
        "best_performing_product": best_performing_product,
        "most_product_in_stock": most_product_in_stock
    }
    
    return render(request, "inventory/dashboard.html", context=context)