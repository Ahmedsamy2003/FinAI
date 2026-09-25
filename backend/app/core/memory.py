from typing import Dict, List


class ConversationMemory:
    """
    Simple in-memory conversation manager.

    Stores conversations using a conversation_id.
    Each conversation contains a list of messages.
    """

    def __init__(self, max_messages: int = 10):
        self.conversations: Dict[str, List[dict]] = {}
        self.max_messages = max_messages

    def get_history(self, conversation_id: str) -> List[dict]:
        """
        Return the conversation history.
        """

        return self.conversations.get(
            conversation_id,
            []
        )

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        """
        Add a message to a conversation.
        """

        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append(
            {
                "role": role,
                "content": content,
            }
        )

        # Keep only the most recent messages
        self.conversations[conversation_id] = (
            self.conversations[conversation_id][-self.max_messages:]
        )

    def clear_conversation(
        self,
        conversation_id: str,
    ):
        """
        Delete a conversation.
        """

        self.conversations.pop(
            conversation_id,
            None,
        )


# Global memory instance
conversation_memory = ConversationMemory(
    max_messages=10
)