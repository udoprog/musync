import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.Toolkit;
import java.awt.Dimension;

import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextArea;

/**
 * Show an error popup.
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
class ErrorPopup extends JFrame implements ActionListener
{
    private JTextArea text;
    private JPanel panel;
    private JButton close;

    /**
     * Constructor, will now build the errori popup but not automatically display it.
     * Use method display to show it.
     */
    public ErrorPopup() {
        super("Error");
        panel = new JPanel();
        close = new JButton("OK");

        text = new JTextArea();
        text.setWrapStyleWord(true);

        text.setEditable(false);
        text.setBackground(null);
        text.setLineWrap(true);

        panel.setLayout(new BorderLayout(2, 0));
        panel.setBorder(BorderFactory.createEmptyBorder(4, 4, 4, 4));

        close.addActionListener(this);

        ImageIcon error_icon = Commons.getImageIcon("gfx/error.png");
        JLabel error_image = new JLabel("", error_icon, JLabel.CENTER);
        panel.add(error_image, BorderLayout.LINE_START);
        panel.add(text, BorderLayout.CENTER);
        panel.add(close, BorderLayout.PAGE_END);

        add(panel);

        setResizable(false);
        setDefaultCloseOperation(JFrame.HIDE_ON_CLOSE);
        Commons.center(this, 200, 140);
    }

    /**
     * What to do when the user presses 'close.'
     *
     * @param e The event.
     */
    public void actionPerformed(ActionEvent e) {
        Object src = e.getSource();
        if (src == close)
            setVisible(false);

        return;
    }
    
    /**
     * Display the popup.
     *
     * @param msg Msg to display with our custom error dialog.
     */
    public void display(String msg)
    {
        setVisible(true);
        text.setText(msg);

        return;
    }
}
