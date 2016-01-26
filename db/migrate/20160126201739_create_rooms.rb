class CreateRooms < ActiveRecord::Migration
  def change
    create_table :rooms do |t|
      t.string :room
      t.string :description
      t.datetime :clock
      t.string :name

      t.timestamps null: false
    end
  end
end
