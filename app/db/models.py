"""
Database Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    embedder = Column(String, nullable=True)
    summarizer = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    chats = relationship("Chat", back_populates="workspace")
    files = relationship("File", back_populates="workspace")
    collections = relationship("Collection", back_populates="workspace")
    assistants = relationship("Assistant", back_populates="workspace")


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    workspace = relationship("Workspace", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    chat_id = Column(String, ForeignKey("chats.id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    model = Column(String, nullable=True)
    token_count = Column(Integer, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chat = relationship("Chat", back_populates="messages")
    file_items = relationship("MessageFileItem", back_populates="message")


class File(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    name = Column(String)
    type = Column(String)
    mime_type = Column(String, nullable=True)
    size = Column(Integer)
    storage_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    workspace = relationship("Workspace", back_populates="files")


class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    embedder = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    workspace = relationship("Workspace", back_populates="collections")
    files = relationship("CollectionFile", back_populates="collection")


class CollectionFile(Base):
    __tablename__ = "collection_files"
    
    id = Column(String, primary_key=True)
    collection_id = Column(String, ForeignKey("collections.id"))
    file_id = Column(String, ForeignKey("files.id"))
    
    collection = relationship("Collection", back_populates="files")
    file = relationship("File")


class Assistant(Base):
    __tablename__ = "assistants"
    
    id = Column(String, primary_key=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    model = Column(String)
    embedder = Column(String, nullable=True)
    tools = Column(JSON, nullable=True)
    file_ids = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    workspace = relationship("Workspace", back_populates="assistants")


class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    name = Column(String)
    type = Column(String)  # openai, anthropic, google, etc.
    key = Column(String)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    display_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MessageFileItem(Base):
    __tablename__ = "message_file_items"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, ForeignKey("messages.id"))
    file_id = Column(String, ForeignKey("files.id"))
    
    message = relationship("Message", back_populates="file_items")
    file = relationship("File")


class Preset(Base):
    __tablename__ = "presets"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    content = Column(Text)
    category = Column(String, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Tool(Base):
    __tablename__ = "tools"
    
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text, nullable=True)
    code = Column(Text)
    schema = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
