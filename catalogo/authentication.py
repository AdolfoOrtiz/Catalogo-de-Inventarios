from rest_framework.authentication import TokenAuthentication

class BearerTokenAuthentication(TokenAuthentication):
    """
    Permite autenticación por token usando la palabra clave 'Bearer'
    además del estándar 'Token' de Django REST Framework.
    
    Ejemplo de Header:
        Authorization: Bearer <tu_token>
        o
        Authorization: Token <tu_token>
    """
    keyword = 'Bearer'
