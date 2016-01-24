class CreatePeople < ActiveRecord::Migration
  def change
    create_table :students do |t|
      t.string :lastname
      t.string :firstname
      t.string :chinesename
      t.date :dob
      t.string :gender
      t.string :countryorigin
      t.string :parentsorigin
      t.string :email
      t.string :mobile
      t.string :occupation
      t.string :fellowship
      t.string :congregation

      t.timestamps null: false
    end
  end
end
