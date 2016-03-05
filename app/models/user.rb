class User < ActiveRecord::Base
  has_many :authorizations
  # Include default devise modules. Others available are:
  # :confirmable, :lockable, :timeoutable and :omniauthable
  devise :database_authenticatable, :registerable,
         :recoverable, :rememberable, :trackable, :validatable, :omniauthable, :omniauth_providers => [:facebook]
  def admin?
    admin
  end

  SOCIALS = {
    facebook: 'Facebook',
    google_oauth2: 'Google',
    linkedin: 'LinkedIn'
  }


  # def self.from_omniauth(auth)
  #   where(provider: auth.provider, uid: auth.uid).first_or_create do |user|
  #     user.provider = auth.provider
  #     user.uid = auth.uid
  #     user.email = auth.info.email
  #     user.password = Devise.friendly_token[0,20]
  #     user.save
  #   end
  # end

  def self.from_omniauth(auth, current_user)
  authorization = Authorization.where(:provider => auth.provider, :uid => auth.uid.to_s,
                                      :token => auth.credentials.token,
                                      :secret => auth.credentials.secret).first_or_initialize
  if auth.info.urls.present?
    authorization.profile_page = auth.info.urls.first.last unless authorization.persisted?
  end

  if authorization.user.blank?
    user = current_user.nil? ? User.where('email = ?', auth['info']['email']).first : current_user
    if user.blank?
      user = User.new
      user.skip_confirmation!
      user.password = Devise.friendly_token[0, 20]
      user.fetch_details(auth)
      user.save
    end
    authorization.user = user
    authorization.save
  end
  authorization.user
end

def fetch_details(auth)
  self.name = auth.info.name
  self.email = auth.info.email
  self.photo = URI.parse(auth.info.image)
end

  def self.new_with_session(params, session)
    super.tap do |user|
      if data = session["devise.facebook_data"] && session["devise.facebook_data"]["extra"]["raw_info"]
        user.email = data["email"] if user.email.blank?
      end
    end
  end
end
