from events.events import SignalEvent


class Format_Text():


	@staticmethod
	def get_format_text_emoji(event: SignalEvent) -> str:

		# Emojis según tipo de señal
		signal_emojis = {
			"buy": "\U0001F7E2",
			"sell": "\U0001F534"
		}

		signal_emoji = signal_emojis.get(event.signal.value.lower(), "⚪")

		# Formato título
		title = f"\U0001F4E3 Señal de trading detectada \U0001F440 : {event.ref}"

		# Formato mensaje
		message = (
			f"\nPosible señal {signal_emoji} {event.signal.value} para {event.symbol}"
			f"\n- \U0001F3AF Precio de objetivo {event.target_price} $."
		)

		# Agrega RSI si existe
		if hasattr(event, 'rsi') and event.rsi is not None:
			rsi_value = round(event.rsi)
			rsi_emoji = "\U0001F525" if rsi_value > 70 or rsi_value < 30 else "\U0001F4A5"
			message += f" \n- {rsi_emoji} RSI {rsi_value}"

		return title, message
	
