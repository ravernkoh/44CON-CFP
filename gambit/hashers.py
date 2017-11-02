from django.contrib.auth.hashers import BCryptSHA256PasswordHasher


class ParanoidBCryptSHA256PasswordHasher(BCryptSHA256PasswordHasher):
    """
    A subclass of BCryptSHA256PasswordHasher to increase iterations
    """

    rounds = BCryptSHA256PasswordHasher.rounds * 1.3
