from telethon.tl.types import (
    MessageReplyHeader,
    MessageReplyStoryHeader,
    PeerChannel,
    PeerChat,
    PeerUser,
)


class MessageProcessor:
    def __init__(self, message):
        """
        Initialize the MessageProcessor with a Telethon message.

        Args:
            message: A Telethon message object.
        """
        self.message = message

    def extract_reactions(self):
        """
        Extract reaction information from the message.

        Returns:
            list: A list of dictionaries containing reaction information.
        """
        reactions = self.message.reactions
        if reactions is None:
            return None

        extracted = []
        for result in reactions.results:
            reaction = {
                "emoticon": (result.reaction.emoticon if hasattr(result.reaction, "emoticon") else None),
                "document_id": (result.reaction.document_id if hasattr(result.reaction, "document_id") else None),
                "count": result.count,
                "chosen_order": (result.chosen_order if hasattr(result, "chosen_order") else None),
            }
            extracted.append(reaction)

        return extracted

    def extract_entity_info(self, entity):
        """
        Extract entity information from the message.

        Args:
            entity: The entity object from the Telethon message.

        Returns:
            dict: A dictionary containing entity information.
        """
        entity_type = type(entity).__name__
        start_index = entity.offset
        end_index = entity.offset + entity.length

        text = self.message.message.encode("utf-16-le")
        start_byte = start_index * 2
        end_byte = end_index * 2
        extracted_text = text[start_byte:end_byte].decode("utf-16-le")

        info = {
            "type": entity_type,
            "pos": {"utf-16-le": {"start": start_index, "end": end_index}},
            "extracted_text": extracted_text,
        }

        if hasattr(entity, "url"):
            info["url"] = entity.url
        if hasattr(entity, "user_id"):
            info["user_id"] = entity.user_id
        if hasattr(entity, "language"):
            info["language"] = entity.language
        if hasattr(entity, "document_id"):
            info["document_id"] = entity.document_id

        return info

    def extract_peer_info(self, peer):
        """
        Extract peer information from the message.

        Args:
            peer: The peer object from the Telethon message.

        Returns:
            dict: A dictionary containing peer information.
        """
        if isinstance(peer, PeerChannel):
            return {"type": "channel", "id": peer.channel_id}
        elif isinstance(peer, PeerUser):
            return {"type": "user", "id": peer.user_id}
        elif isinstance(peer, PeerChat):
            return {"type": "chat", "id": peer.chat_id}
        else:
            return str(peer)

    def extract_fwd_header(self):
        """
        Extract forward header information from the message.

        Returns:
            dict: A dictionary containing forward header information.
        """
        fwd_from = self.message.fwd_from
        if not fwd_from:
            return None

        fwd_info = {
            "date": fwd_from.date.isoformat() if fwd_from.date else None,
            "imported": fwd_from.imported,
            "saved_out": fwd_from.saved_out,
            "from_id": (self.extract_peer_info(fwd_from.from_id) if fwd_from.from_id else None),
            "from_name": fwd_from.from_name,
            "channel_post": fwd_from.channel_post,
            "post_author": fwd_from.post_author,
            "saved_from_peer": (
                self.extract_peer_info(fwd_from.saved_from_peer) if fwd_from.saved_from_peer else None
            ),
            "saved_from_msg_id": fwd_from.saved_from_msg_id,
            "saved_from_id": (self.extract_peer_info(fwd_from.saved_from_id) if fwd_from.saved_from_id else None),
            "saved_from_name": fwd_from.saved_from_name,
            "saved_date": (fwd_from.saved_date.isoformat() if fwd_from.saved_date else None),
            "psa_type": fwd_from.psa_type,
        }
        return {k: v for k, v in fwd_info.items() if v is not None}

    def extract_reply_header(self):
        """
        Extract reply header information from the message.

        Returns:
            dict: A dictionary containing reply header information.
        """
        reply_to = self.message.reply_to
        if not reply_to:
            return None

        if isinstance(reply_to, MessageReplyHeader):
            reply_info = {
                "reply_to_scheduled": reply_to.reply_to_scheduled,
                "forum_topic": reply_to.forum_topic,
                "quote": reply_to.quote,
                "reply_to_msg_id": reply_to.reply_to_msg_id,
                "reply_to_peer_id": (
                    self.extract_peer_info(reply_to.reply_to_peer_id) if reply_to.reply_to_peer_id else None
                ),
                "reply_from": (self.extract_fwd_header() if reply_to.reply_from else None),
                "reply_media": (str(reply_to.reply_media) if reply_to.reply_media else None),
                "reply_to_top_id": reply_to.reply_to_top_id,
                "quote_text": reply_to.quote_text,
                "quote_entities": (
                    [self.extract_entity_info(entity) for entity in reply_to.quote_entities]
                    if reply_to.quote_entities
                    else None
                ),
                "quote_offset": reply_to.quote_offset,
            }
        elif isinstance(reply_to, MessageReplyStoryHeader):
            reply_info = {
                "type": "story",
                "peer": self.extract_peer_info(reply_to.peer),
                "story_id": reply_to.story_id,
            }
        else:
            reply_info = str(reply_to)

        return {k: v for k, v in reply_info.items() if v is not None}

    def process(self):
        """
        Process the Telethon message and extract relevant information.

        Returns:
            dict: A dictionary containing processed message information.
        """
        entities = [
            {
                "entity": self.extract_entity_info(entity),
                "text": text,
            }
            for entity, text in self.message.get_entities_text()
        ]

        return {
            "id": self.message.id,
            "date": self.message.date.isoformat(),
            "message": self.message.message,
            "entities": entities,
            "fwd_from": self.extract_fwd_header(),
            "reply_to": self.extract_reply_header(),
            "views": self.message.views,
            "reactions": self.extract_reactions(),
        }
