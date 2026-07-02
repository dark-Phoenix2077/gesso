from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import Enum, UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

db = SQLAlchemy()

import enum

class UserRole(enum.Enum):
    ARTIST = "ARTIST"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class ArtworkStatus(enum.Enum):
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Visibility(enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    UNLISTED = "UNLISTED"

class CompetitionStatus(enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    VOTING = "VOTING"
    CLOSED = "CLOSED"

class BadgeTier(enum.Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    SPECIAL = "SPECIAL"


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    displayName: Mapped[str] = mapped_column(nullable=True)
    passwordHash: Mapped[str] = mapped_column(nullable=True)  # nullable for pure OAuth users
    avatarUrl: Mapped[str] = mapped_column(nullable=True)
    bio: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.ARTIST, nullable=False)
    tier: Mapped[str] = mapped_column(nullable=True)
    totalLikesReceived: Mapped[int] = mapped_column(default=0, nullable=False)
    totalArtworks: Mapped[int] = mapped_column(default=0, nullable=False)
    isVerified: Mapped[bool] = mapped_column(default=False, nullable=False)
    isBanned: Mapped[bool] = mapped_column(default=False, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    artworks = relationship("Artwork", back_populates="author", lazy="dynamic")
    portfolio = relationship("Portfolio", back_populates="user", uselist=False)
    badges = relationship("UserBadge", back_populates="user", lazy="dynamic")

    # Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return not self.isBanned

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


class Artwork(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    imageUrl: Mapped[str] = mapped_column(nullable=False)
    thumbnailUrl: Mapped[str] = mapped_column(nullable=True)
    medium: Mapped[str] = mapped_column(nullable=True)
    styleTags: Mapped[list] = mapped_column(JSON, nullable=True)  # list of strings
    authorId: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[ArtworkStatus] = mapped_column(
        Enum(ArtworkStatus), default=ArtworkStatus.DRAFT, nullable=False
    )
    visibility: Mapped[Visibility] = mapped_column(
        Enum(Visibility), default=Visibility.PUBLIC, nullable=False
    )
    likeCount: Mapped[int] = mapped_column(default=0, nullable=False)
    saveCount: Mapped[int] = mapped_column(default=0, nullable=False)
    viewCount: Mapped[int] = mapped_column(default=0, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updatedAt: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    author = relationship("User", back_populates="artworks")


class Portfolio(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    artworkIds: Mapped[list] = mapped_column(JSON, nullable=True)
    isPublic: Mapped[bool] = mapped_column(default=True, nullable=False)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="portfolio")


class Competition(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    theme: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)
    rules: Mapped[str] = mapped_column(nullable=True)
    prizes: Mapped[dict] = mapped_column(JSON, nullable=True)
    status: Mapped[CompetitionStatus] = mapped_column(
        Enum(CompetitionStatus), default=CompetitionStatus.DRAFT, nullable=False
    )
    startDate: Mapped[datetime] = mapped_column(nullable=True)
    endDate: Mapped[datetime] = mapped_column(nullable=True)
    createdByAdminId: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    coverImageUrl: Mapped[str] = mapped_column(nullable=True)

    createdByAdmin = relationship("User")


class CompetitionEntry(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    competitionId: Mapped[int] = mapped_column(ForeignKey("competition.id"), nullable=False)
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    artworkId: Mapped[int] = mapped_column(ForeignKey("artwork.id"), nullable=False)
    communityVotes: Mapped[int] = mapped_column(default=0, nullable=False)
    judgeScore: Mapped[float] = mapped_column(nullable=True)
    finalRank: Mapped[int] = mapped_column(nullable=True)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)


class Badge(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    iconUrl: Mapped[str] = mapped_column(nullable=True)
    criteria: Mapped[dict] = mapped_column(JSON, nullable=True)
    tier: Mapped[BadgeTier] = mapped_column(Enum(BadgeTier), nullable=False)


class UserBadge(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    badgeId: Mapped[int] = mapped_column(ForeignKey("badge.id"), nullable=False)
    awardedAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge")


class Follow(db.Model):
    followerId: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    followingId: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("followerId", "followingId", name="uq_follow"),
    )


class Like(db.Model):
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    artworkId: Mapped[int] = mapped_column(ForeignKey("artwork.id"), primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)


class Save(db.Model):
    userId: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    artworkId: Mapped[int] = mapped_column(ForeignKey("artwork.id"), primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)