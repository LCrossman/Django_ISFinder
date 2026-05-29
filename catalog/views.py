from django.http import HttpResponse
from .models import ISElement

#index function
def index(request):
    total_elements = ISElement.objects.count()
    return HttpResponse(f"Welcome to the IS Catalog! There are {total_elements} elements in the database.")

def elements_by_origin(request, origin_name):
    #filter the database for the specific origin
    elements = ISElement.objects.filter(origin__name=origin_name)
    
    #start building the HTML string
    html_content = f"<h1>Origin: {origin_name}</h1>"
    html_content += f"<p><strong>Total IS elements found:</strong> {elements.count()}</p>"
    html_content += "<ul>"
    
    #loop through each element for the Name, Family, and Group
    for el in elements:
        #check if the family exists, otherwise Unknown
        family_name = el.family.name if el.family else "Unknown"
        
        #check if the group exists (since many were 'NA' or empty), otherwise "None"
        group_name = el.group.name if el.group else "None"
        
        #add a bullet point for this element
        html_content += f"<li><strong>{el.name}</strong> — Family: {family_name} | Group: {group_name}</li>"
    
    html_content += "</ul>"
    
    return HttpResponse(html_content)
