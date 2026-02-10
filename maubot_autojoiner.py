from maubot import Plugin
from maubot.handlers import event
from mautrix.types import EventType, Membership, StateEvent
from mautrix.util.config import BaseProxyConfig

class Config(BaseProxyConfig):
    def do_update(self, helper):
        helper.copy("space_id")
        helper.copy("auto_join_rooms")

class AutoJoinerBot(Plugin):

    @classmethod
    def get_config_class(cls):
        return Config

    async def start(self) -> None:
        await super().start()
        self.config.load_and_update()
        self.space_id = self.config["space_id"]
        self.auto_join_rooms = self.config["auto_join_rooms"]
    
    @event.on(EventType.ROOM_MEMBER, is_state=True)
    async def member_handler(self, evt: StateEvent) -> None:
        # Only handle events in our configured space
        if evt.room_id != self.space_id:
            return
            
        # Only handle new joins
        if evt.content.membership != Membership.JOIN:
            return
        
        # Don't process our own joins
        if evt.state_key == self.client.mxid:
            return
            
        user_id = evt.state_key
        
        # Invite to all configured rooms
        for room_id in self.auto_join_rooms:
            try:
                await self.client.invite_user(room_id, user_id)
                self.log.info(f"Invited {user_id} to {room_id}")
            except Exception as e:
                self.log.warning(f"Failed to invite {user_id} to {room_id}: {e}")