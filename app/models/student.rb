class Student < ActiveRecord::Base
  has_attached_file :image, styles: {large: "1920x1080#", medium: "800x500#", thumb: "100x100"}, :default_url => "/images/:style/missing.png"
  validates_attachment_content_type :image, :content_type => ["image/jpg", "image/jpeg", "image/png", "image/gif"]

  def age()
    now = Time.now.utc.to_date
    return now.year - self.dob.year - ((now.month > self.dob.month || (now.month == self.dob.month && now.day >= self.dob.day)) ? 0 : 1)
  end
end
