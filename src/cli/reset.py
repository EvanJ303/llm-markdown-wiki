from storage import Vault


def reset(vault: Vault) -> None:
	try:
		vault.reset()
		print("Vault reset successfully.")
	except Exception as e:
		print(f"Error resetting vault: {e}")
