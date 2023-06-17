from django import template

register = template.Library()


@register.filter(name="is_coach")
def is_coach(self):
    user_is_coach = self.user.member.is_coach
    return user_is_coach
