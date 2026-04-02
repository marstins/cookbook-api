from app.domain.models.aggregates.user import User, UserPublic


class UserPublicMapper:
    def map_to_public(self, user: User) -> UserPublic:
        return UserPublic(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at,
        )
