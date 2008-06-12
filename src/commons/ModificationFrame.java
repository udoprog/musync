import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

/**
 * Shows the popup window where the user can change default temorary meta data for
 * items being addded.
 *
 * Copyright: John-John Tedro, Oscar Eriksson (2008)
 *
 *   This file is part of musync-swing.
 *
 *   musync-swing is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   musync-swing is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with musync-swing.  If not, see <http://www.gnu.org/licenses/>.
 */
class ModificationFrame extends JFrame implements ActionListener
{
    private JTextPane artist, album, title, track;
    private JButton close;
    private JTextArea desc;

    private JPanel input;
    
    private static final String DESCRIPTION =
        "Musync will use the metadata values you set here instead of "
        + "the ones found in files you are trying to add\n"
        + "note: this will not overwrite the current metadata";

    /**
     * Constructor will create the popup, but not show it until method
     * 'display' has been called.
     */
    public ModificationFrame()
    {
        super("Modify Metadata (temporary)");

        getRootPane().setBorder(BorderFactory.createEmptyBorder(4,4,4,4));

        setLayout(new BorderLayout());
        input = new JPanel();
        input.setLayout(new GridLayout(4,2,2,2));
        input.setBorder(BorderFactory.createEmptyBorder(4,4,4,4));

        close = new JButton("close");
        close.addActionListener(this);

        buildDescription();
        buildInputPanes();
        
        input.add(new JLabel("Artist"));
        input.add(artist);
        input.add(new JLabel("Album"));
        input.add(album);
        input.add(new JLabel("Title"));
        input.add(title);
        input.add(new JLabel("Track"));
        input.add(track);

        add(input, BorderLayout.CENTER);
        add(close, BorderLayout.PAGE_END);
        add(desc, BorderLayout.PAGE_START);

        setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
        setResizable(true);
        setVisible(false);
        setSize(400,188);
        Commons.center(this,400,188);
    }

    /**
     * Create all input panes.
     */
    private void buildInputPanes()
    {
        Color black = new Color(0,0,0);
        artist = new JTextPane();
        artist.setBorder(BorderFactory.createLineBorder(black));
        album = new JTextPane();
        album.setBorder(BorderFactory.createLineBorder(black));
        title = new JTextPane();
        title.setBorder(BorderFactory.createLineBorder(black));
        track = new JTextPane();
        track.setBorder(BorderFactory.createLineBorder(black));

        return;
    }

    /**
     * Build the description text area.
     */
    private void buildDescription()
    {
        desc = new JTextArea();
        desc.setRows(3);
        desc.setLineWrap(true);
        desc.setWrapStyleWord(true);
        desc.setText(DESCRIPTION);
        desc.setEditable(false);
        desc.setBackground(null);

        return;
    }
   
    /**
     * What to do when the user presses the 'close' button.
     *
     * @param e The event.
     */
    public void actionPerformed(ActionEvent e)
    {
        if (e.getSource() == close) {
            setVisible(false);
        }

        return;
    }

    /**
     * Display the popup.
     */
    public void display()
    {
        setVisible(true);

        return;
    }

    /**
     * Return all the things that the user has entered in the fields.
     *
     * @return An array of the user's inputs.
     */
    public String[] serialize()
    {
        int c = 0;

        String artist_s = artist.getText();
        String album_s = album.getText();
        String title_s = title.getText();
        String track_s = track.getText();

        if (!artist_s.equals(""))
            c++;
        if (!album_s.equals(""))
            c++;
        if (!title_s.equals(""))
            c++;
        if (!track_s.equals(""))
            c++;

        String[] ser = new String[c*2];
        
        c = 0;
        if (!artist_s.equals("")) {
            ser[c++] = "-M";
            ser[c++] = "artist=\"" + artist_s + "\"";
        }
        
        if (!album_s.equals("")) {
            ser[c++] = "-M";
            ser[c++] = "album=\"" + album_s + "\"";
            c++;
        }
        
        if (!title_s.equals("")) {
            ser[c++] = "-M";
            ser[c++] = "title=\"" + title_s + "\"";
            c++;
        }
        
        if (!track_s.equals("")) {
            ser[c++] = "-M";
            ser[c++] = "track=\"" + track_s + "\"";
        }

        return ser;
    }
}
