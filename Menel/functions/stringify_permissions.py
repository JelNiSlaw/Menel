import discord


def stringify_permissions(permissions: discord.Permissions) -> str:
    return ', '.join(f'`{perm.replace("_", " ")}`' for perm, value in iter(permissions) if value)