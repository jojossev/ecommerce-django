from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Panier, ArticlePanier
from catalog.models import Produit

@login_required
def vue_panier(request):
    """Affiche le contenu du panier de l'utilisateur connecté."""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    articles = panier.items.select_related('produit').all()
    
    context = {
        'panier': panier,
        'articles': articles,
    }
    return render(request, 'cart/panier.html', context)

@login_required
@require_POST
def ajouter_au_panier(request, produit_id):
    """Ajoute un produit au panier."""
    produit = get_object_or_404(Produit, id=produit_id, est_actif=True)
    quantite = int(request.POST.get('quantite', 1))
    
    # Vérifie si le produit est déjà dans le panier
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    article, created = ArticlePanier.objects.get_or_create(
        panier=panier,
        produit=produit,
        defaults={'quantite': quantite, 'prix_unitaire': produit.prix}
    )
    
    if not created:
        # Si l'article existe déjà, on met à jour la quantité
        article.quantite += quantite
        article.save()
    
    # Préparer la réponse
    response_data = {
        'success': True,
        'message': f"{produit.nom} a été ajouté à votre panier.",
        'nombre_articles': panier.nombre_articles,
        'sous_total': float(article.sous_total)
    }
    
    # Si c'est une requête AJAX, on renvoie du JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(response_data)
    
    # Sinon, on redirige normalement
    messages.success(request, response_data['message'])
    return redirect(request.META.get('HTTP_REFERER', 'cart:panier'))

@login_required
@require_POST
def mettre_a_jour_panier(request, article_id):
    """Met à jour la quantité d'un article dans le panier."""
    article = get_object_or_404(ArticlePanier, id=article_id, panier__utilisateur=request.user)
    quantite = int(request.POST.get('quantite', 1))
    
    if quantite > 0:
        article.quantite = quantite
        article.save()
        messages.success(request, "La quantité a été mise à jour.")
    else:
        article.delete()
        messages.success(request, "L'article a été retiré de votre panier.")
    
    return redirect('cart:panier')

@login_required
@require_POST
def supprimer_du_panier(request, article_id):
    """Supprime un article du panier."""
    article = get_object_or_404(ArticlePanier, id=article_id, panier__utilisateur=request.user)
    nom_produit = article.produit.nom
    article.delete()
    
    messages.success(request, f"{nom_produit} a été retiré de votre panier.")
    return redirect('cart:panier')

@login_required
def nombre_articles_panier(request):
    """Retourne le nombre d'articles dans le panier (pour l'API AJAX)."""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    return JsonResponse({'nombre_articles': panier.nombre_articles})
